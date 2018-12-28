package io.flywheel.codegen;

import io.swagger.codegen.*;
import io.swagger.models.Model;
import io.swagger.models.Operation;
import io.swagger.models.Path;
import io.swagger.models.Swagger;
import io.swagger.models.properties.Property;

import java.util.*;

public class FlywheelCodegenSupport {


    public static void preprocessSwagger(Swagger swagger) {
        preprocessSwaggerModels(swagger);
        removeExtraOperationTags(swagger);
    }

    public static void removeSupportingFile(List<SupportingFile> supportingFiles, String name) {
        Iterator<SupportingFile> itr = supportingFiles.iterator();
        while(itr.hasNext()) {
            SupportingFile file = itr.next();
            if( file.templateFile.equals(name) ) {
                itr.remove();
                break;
            }
        }
    }

    private static void preprocessSwaggerModels(Swagger swagger) {
        Map<String, Model> models = swagger.getDefinitions();
        for( String name : models.keySet() ) {
            Model model = models.get(name);
            Map<String, Object> vendorExtensions = model.getVendorExtensions();
            if( vendorExtensions != null ) {
                if( vendorExtensions.containsKey("x-sdk-ignore-properties") ) {
                    List<String> ignoredProperties = (List<String>)(vendorExtensions.get("x-sdk-ignore-properties"));
                    Map<String, Property> properties = model.getProperties();
                    if( properties != null ) {
                        for( String property: ignoredProperties ) {
                            properties.remove(property);
                        }
                    }
                }
            }
        }
    }

    private static void removeExtraOperationTags(Swagger swagger) {
        Map<String,Path> paths = swagger.getPaths();
        for( String path: paths.keySet() ) {
            Path pathEntry = paths.get(path);
            for(Operation operation: pathEntry.getOperations()) {
                List<String> tags = operation.getTags();
                if( tags != null && tags.size() > 1 ) {
                    operation.setTags(Arrays.asList(tags.get(0)));
                }
            }
        }
    }

    public static Map<String, Object> postProcessModels(Map<String, Object> objs, DefaultCodegen gen) {
        ArrayList<Object> modelsArray = (ArrayList<Object>) objs.get("models");
        Map<String, Object> models = (Map<String, Object>) modelsArray.get(0);
        CodegenModel model = (CodegenModel) models.get("model");

        final Map<String, String> typeMapping = gen.typeMapping();
        if( typeMapping == null ) {
            return objs;
        }

        // If the model includes a list of "x-sdk-include-empty" properties, then we need to
        // push that to the individual properties. (If the properties reference other types then the
        // vendorExtensions don't get picked up)
        if( model.vendorExtensions != null ) {
            if( model.vendorExtensions.containsKey("x-sdk-include-empty") ) {
                List<String> emptyProps = (List<String>) model.vendorExtensions.get("x-sdk-include-empty");
                for (String propName : emptyProps) {
                    CodegenProperty prop = findPropertyByName(model, propName);
                    if (prop != null) {
                        if (prop.vendorExtensions == null) {
                            prop.vendorExtensions = new HashMap<>();
                        }
                        prop.vendorExtensions.put("x-sdk-include-empty", true);
                    }
                }
            }

            if( model.vendorExtensions.containsKey("x-sdk-container-mixin") ) {
                // Convert model name
                String mixinName = (String)model.vendorExtensions.get("x-sdk-container-mixin");
                model.vendorExtensions.put("x-sdk-container-mixin", gen.toModelName(mixinName));
            }
        }

        // Additionally, if a parameter has x-sdk-positional set to true, then set x-sdk-positional-param on model
        for( CodegenProperty prop : model.allVars ) {
            if( prop.vendorExtensions != null && prop.vendorExtensions.containsKey("x-sdk-positional") ) {
                model.vendorExtensions.put("x-sdk-positional-param", prop.name);
            }
        }

        return objs;
    }

    public static Map<String, Object> postProcessOperations(Map<String, Object> objs, DefaultCodegen gen) {
        Map<String, Object> operations = (Map<String, Object>)objs.get("operations");
        if( operations == null ) {
            return objs;
        }

        List<CodegenOperation> ops = (List<CodegenOperation>)operations.get("operation");
        int size = ops.size();
        int idx = 0;
        while( idx < size ) {
            CodegenOperation op = ops.get(idx);
            if( op.vendorExtensions != null ) {
                if( op.vendorExtensions.containsKey("x-sdk-get-zip-info") ) {
                    CodegenOperation newOp = createGetZipInfoOp(op, gen);
                    if (newOp != null) {
                        ops.add(idx + 1, newOp);
                        idx += 1;
                        size += 1;
                    }
                }

                if( op.vendorExtensions.containsKey("x-sdk-download-ticket") ) {
                    CodegenOperation newOp = createDownloadTicketOp(op, gen);
                    if (newOp != null) {
                        ops.add(idx + 1, newOp);
                        idx += 1;
                        size += 1;
                    }
                } else if( op.vendorExtensions.containsKey("x-sdk-modify-info") ) {
                    // Convert to an array of the 3 operations
                    op.vendorExtensions.put("x-sdk-modify-wrapper", makeModifyInfoWrappers(op.operationIdSnakeCase, gen));
                } else if( op.vendorExtensions.containsKey("x-sdk-modify-classification") ) {
                    // Convert to an array of the 3 operations
                    op.vendorExtensions.put("x-sdk-modify-wrapper", makeModifyClassificationWrappers(op.operationIdSnakeCase, gen));
                } else if( op.vendorExtensions.containsKey("x-sdk-download-file-param") ) {
                    String paramName = op.vendorExtensions.get("x-sdk-download-file-param").toString();
                    op.vendorExtensions.put("x-sdk-download-file-param", gen.toParamName(paramName));

                    // Update the response as well, so that the download handler is generated for matlab
                    for(int i = 0; i < op.responses.size(); i++ ) {
                        CodegenResponse resp = op.responses.get(i);
                        if( "200".equals(resp.code) ) {
                            resp.vendorExtensions.put("x-sdk-download-file-param", gen.toParamName(paramName));
                        }
                    }
                }
            }
            ++idx;
        }

        return objs;
    }

    private static CodegenOperation createDownloadTicketOp(CodegenOperation orig, DefaultCodegen gen) {
        String operationId = (String)orig.vendorExtensions.get("x-sdk-download-ticket");
        String getDownloadUrlId = makeDownloadUrlId(operationId);

        operationId = gen.toOperationId(operationId);
        getDownloadUrlId = gen.toOperationId(getDownloadUrlId);

        orig.vendorExtensions.remove("x-sdk-download-ticket");

        CodegenOperation newOp = shallowCloneOperation(orig);

        // Find the 200 response
        int responseIdx = 0;
        CodegenResponse response = null;
        for( ; responseIdx < orig.responses.size(); responseIdx++ ) {
            CodegenResponse resp = orig.responses.get(responseIdx);
            if( "200".equals(resp.code) ) {
                response = resp;
                break;
            }
        }

        // At this point the new op is the ticket operation
        newOp.operationId = operationId;
        newOp.operationIdLowerCase = DefaultCodegen.camelize(operationId, true);
        newOp.operationIdCamelCase = DefaultCodegen.camelize(operationId);
        newOp.operationIdSnakeCase = gen.snakeCase(operationId);

        newOp.produces = new ArrayList<>();
        newOp.produces.add(makeMediaType("application/json", false));

        newOp.vendorExtensions.put("x-sdk-download-url", getDownloadUrlId);

        // And orig is the download operation
        orig.produces = new ArrayList<>();
        orig.produces.add(makeMediaType("application/octet-stream", false));

        String destFileParam = gen.toVarName("dest-file");
        orig.vendorExtensions.put("x-sdk-download-file-param", destFileParam);

        removeQueryParam(orig, "ticket");

        // Update the response on the original
        if( response != null ) {
            CodegenResponse fileResp = shallowCloneResponse(response);
            orig.responses.set(responseIdx, fileResp);

            fileResp.isFile = true;
            fileResp.simpleType = false;
            fileResp.primitiveType = false;

            fileResp.dataType = null;
            fileResp.baseType = null;
            fileResp.containerType = null;

            fileResp.vendorExtensions.put("x-sdk-download-file-param", destFileParam);
        }

        return newOp;
    }

    private static CodegenOperation createGetZipInfoOp(CodegenOperation orig, DefaultCodegen gen) {
        // Does not modify the original request
        String operationId = (String)orig.vendorExtensions.get("x-sdk-get-zip-info");
        String returnType = gen.toModelName("file-zip-info");

        operationId = gen.toOperationId(operationId);

        orig.vendorExtensions.remove("x-sdk-get-zip-info");

        CodegenOperation newOp = shallowCloneOperation(orig);

        // At this point the new op is the ticket operation
        newOp.operationId = operationId;
        newOp.operationIdLowerCase = DefaultCodegen.camelize(operationId, true);
        newOp.operationIdCamelCase = DefaultCodegen.camelize(operationId);
        newOp.operationIdSnakeCase = gen.snakeCase(operationId);

        newOp.produces = new ArrayList<>();
        newOp.produces.add(makeMediaType("application/json", false));

        newOp.returnType = returnType;
        newOp.returnBaseType = returnType;

        // set default query parameter
        updateQueryParam(newOp, "info", new UpdateParameterOp() {
            @Override
            public void update(CodegenParameter param) {
                if( param.vendorExtensions == null ) {
                    param.vendorExtensions = new HashMap<>();
                }
                param.vendorExtensions.put("x-sdk-default", "true");
            }
        }, true);

        // Find and update the 200 response
        int responseIdx = 0;
        CodegenResponse response = null;
        for( ; responseIdx < orig.responses.size(); responseIdx++ ) {
            CodegenResponse resp = orig.responses.get(responseIdx);
            if( "200".equals(resp.code) ) {
                response = resp;
                break;
            }
        }

        if( response != null ) {
            CodegenResponse fileResp = shallowCloneResponse(response);
            newOp.responses.set(responseIdx, fileResp);

            fileResp.simpleType = false;
            fileResp.primitiveType = true;

            fileResp.dataType = returnType;
            fileResp.baseType = returnType;
            fileResp.containerType = null;
        }

        return newOp;
    }

    private static String makeDownloadUrlId(String operationId) {
        return operationId.replace("_ticket", "_url");
    }

    private static List<Map<String, Object>> makeModifyInfoWrappers(String operationId, DefaultCodegen gen) {
        return makeModifyWrappers(operationId, gen, "info", "set");
    }

    private static List<Map<String, Object>> makeModifyClassificationWrappers(String operationId, DefaultCodegen gen) {
        return makeModifyWrappers(operationId, gen, "classification", "add");
    }

    private static List<Map<String, Object>> makeModifyWrappers(String operationId, DefaultCodegen gen, String name, String setKey) {
        List<Map<String, Object>> result = new ArrayList<>();

        // Set
        String opId = operationId.replace("modify_", "set_");
        Map<String, Object> detail = new HashMap<>();
        detail.put("wrapperId", gen.toOperationId(opId));
        detail.put("summary", "Update " + name + " with the provided fields.");
        detail.put("key", setKey);
        result.add(detail);

        // Replace
        opId = operationId.replace("modify_", "replace_");
        detail = new HashMap<>();
        detail.put("wrapperId", gen.toOperationId(opId));
        detail.put("summary", "Entirely replace " + name + " with the provided fields.");
        detail.put("key", "replace");
        result.add(detail);

        // Delete
        opId = operationId.replace("modify_", "delete_") + "_fields";
        detail = new HashMap<>();
        detail.put("wrapperId", gen.toOperationId(opId));
        detail.put("summary", "Delete the specified fields from  + name + .");
        detail.put("key", "delete");
        result.add(detail);

        return result;
    }

    // ugh
    private static CodegenOperation shallowCloneOperation(CodegenOperation orig) {
        CodegenOperation result = new CodegenOperation();

        result.responseHeaders.addAll(orig.responseHeaders);

        result.hasAuthMethods = orig.hasAuthMethods;
        result.hasConsumes = orig.hasConsumes;
        result.hasProduces = orig.hasProduces;
        result.hasParams = orig.hasParams;
        result.hasOptionalParams = orig.hasOptionalParams;
        result.hasRequiredParams = orig.hasRequiredParams;
        result.returnTypeIsPrimitive = orig.returnTypeIsPrimitive;
        result.returnSimpleType = orig.returnSimpleType;
        result.subresourceOperation = orig.subresourceOperation;
        result.isMapContainer = orig.isMapContainer;
        result.isListContainer = orig.isListContainer;
        result.isMultipart = orig.isMultipart;
        result.hasMore = orig.hasMore;
        result.isResponseBinary = orig.isResponseBinary;
        result.isResponseFile = orig.isResponseFile;
        result.hasReference = orig.hasReference;
        result.isRestfulIndex = orig.isRestfulIndex;
        result.isRestfulShow = orig.isRestfulShow;
        result.isRestfulCreate = orig.isRestfulCreate;
        result.isRestfulUpdate = orig.isRestfulUpdate;
        result.isRestfulDestroy = orig.isRestfulDestroy;
        result.isRestful = orig.isRestful;
        result.isDeprecated = orig.isDeprecated;

        result.path = orig.path;
        result.operationId = orig.operationId;
        result.returnType = orig.returnType;
        result.httpMethod = orig.httpMethod;
        result.returnBaseType = orig.returnBaseType;
        result.returnContainer = orig.returnContainer;
        result.summary = orig.summary;
        result.unescapedNotes = orig.unescapedNotes;
        result.notes = orig.notes;
        result.baseName = orig.baseName;
        result.defaultResponse = orig.defaultResponse;
        result.discriminator = orig.discriminator;

        if( orig.consumes != null ) {
            result.consumes = new ArrayList<>(orig.consumes);
        }
        if( orig.produces != null ) {
            result.produces = new ArrayList<>(orig.produces);
        }
        if( orig.prioritizedContentTypes != null ) {
            result.prioritizedContentTypes = new ArrayList<>(orig.prioritizedContentTypes);
        }

        result.bodyParam = orig.bodyParam;

        result.allParams.addAll(orig.allParams);
        result.bodyParams.addAll(orig.bodyParams);

        result.pathParams.addAll(orig.pathParams);
        result.queryParams.addAll(orig.queryParams);
        result.headerParams.addAll(orig.headerParams);
        result.formParams.addAll(orig.formParams);
        result.requiredParams.addAll(orig.requiredParams);

        if (orig.authMethods != null) {
            result.authMethods = new ArrayList<>(orig.authMethods);
        }

        if (orig.tags != null) {
            result.tags = new ArrayList<>(orig.tags);
        }

        result.responses.addAll(orig.responses);
        result.imports.addAll(orig.imports);

        if (orig.examples != null) {
            result.examples = new ArrayList<>(orig.examples);
        }

        if (orig.requestBodyExamples != null) {
            result.requestBodyExamples = new ArrayList<>(orig.requestBodyExamples);
        }

        result.externalDocs = orig.externalDocs;

        if (orig.vendorExtensions != null) {
            result.vendorExtensions = new HashMap<>(orig.vendorExtensions);
        }

        result.operationIdLowerCase = orig.operationIdLowerCase;
        result.operationIdCamelCase = orig.operationIdCamelCase;
        result.operationIdSnakeCase = orig.operationIdSnakeCase;

        return result;
    }

    private static CodegenResponse shallowCloneResponse(CodegenResponse orig) {
        CodegenResponse result = new CodegenResponse();

        result.headers.addAll(orig.headers);

        result.code = orig.code;
        result.message = orig.message;

        result.hasMore = orig.hasMore;
        if( orig.examples != null ) {
            result.examples = new ArrayList<>(orig.examples);
        }

        result.dataType = orig.dataType;
        result.baseType = orig.baseType;
        result.containerType = orig.containerType;

        result.hasHeaders = orig.hasHeaders;
        result.isString = orig.isString;
        result.isNumeric = orig.isNumeric;
        result.isInteger = orig.isInteger;
        result.isLong = orig.isLong;
        result.isNumber = orig.isNumber;
        result.isFloat = orig.isFloat;
        result.isDouble = orig.isDouble;
        result.isByteArray = orig.isByteArray;
        result.isBoolean = orig.isBoolean;
        result.isDate = orig.isDate;
        result.isDateTime = orig.isDateTime;
        result.isUuid = orig.isUuid;

        result.isDefault = orig.isDefault;
        result.simpleType = orig.simpleType;
        result.primitiveType = orig.primitiveType;
        result.isMapContainer = orig.isMapContainer;
        result.isListContainer = orig.isListContainer;
        result.isBinary = orig.isBinary;
        result.isFile = orig.isFile;

        result.schema = orig.schema;
        result.jsonSchema = orig.jsonSchema;

        if( orig.vendorExtensions != null ) {
            result.vendorExtensions = new HashMap<>(orig.vendorExtensions);
        }

        return result;
    }

    private static Map<String, String> makeMediaType(String mediaType, boolean hasMore) {
        Map<String, String> result = new HashMap<>();

        result.put("mediaType", mediaType);
        if( hasMore ) {
            result.put("hasMore", "true");
        } else {
            result.put("hasMore", null);
        }

        return result;
    }

    private static void removeQueryParam(CodegenOperation op, String name) {
        removeQueryParamFromList(op.allParams, name);
        removeQueryParamFromList(op.queryParams, name);
        removeQueryParamFromList(op.requiredParams, name);
    }

    private static void removeQueryParamFromList(List<CodegenParameter> params, String name) {
        Iterator<CodegenParameter> itr = params.iterator();
        while( itr.hasNext() ) {
            CodegenParameter param = itr.next();
            if( param.isQueryParam && name.equals(param.baseName) ) {
                itr.remove();
                break;
            }
        }
    }


    private static void updateQueryParam(CodegenOperation op, String name, UpdateParameterOp update, boolean copy) {
        updateQueryParamInList(op.allParams, name, update, copy);
        updateQueryParamInList(op.queryParams, name, update, copy);
        updateQueryParamInList(op.requiredParams, name, update, copy);
    }

    private static void updateQueryParamInList(List<CodegenParameter> params, String name, UpdateParameterOp update, boolean copy) {
        for( int i = 0; i < params.size(); i++ ) {
            CodegenParameter param = params.get(i);
            if( param.isQueryParam && name.equals(param.baseName) ) {
                // Replace with copy
                if( copy ) {
                    param = param.copy();
                    params.remove(i);
                    params.add(i, param);
                }

                update.update(param);
                break;
            }
        }
    }

    private static CodegenProperty findPropertyByName(CodegenModel model, String property) {
        for( CodegenProperty prop: model.allVars ) {
            if( property.equals(prop.baseName) ) {
                return prop;
            }
        }
        return null;
    }
}
