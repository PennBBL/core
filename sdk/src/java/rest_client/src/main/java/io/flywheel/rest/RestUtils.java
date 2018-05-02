package io.flywheel.rest;

import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.NameValuePair;
import org.apache.commons.httpclient.URIException;
import org.apache.commons.httpclient.methods.*;
import org.apache.commons.httpclient.methods.multipart.*;
import org.apache.commons.httpclient.util.EncodingUtil;
import org.apache.commons.httpclient.util.URIUtil;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.net.FileNameMap;
import java.net.URLConnection;
import java.util.Map;
import java.util.TreeMap;

public class RestUtils {

    public static final String FORM_URL_ENCODED_CONTENT_TYPE = "application/x-www-form-urlencoded";

    public static final String DEFAULT_MIME_TYPE = "application/octet-stream";

    private static Map<String, Constructor<? extends HttpMethod>> METHOD_MAP;

    private static FileNameMap FILE_NAME_MAP = URLConnection.getFileNameMap();

    private static final String DEFAULT_FILE_TYPE = "application/octet-stream";

    static {
        METHOD_MAP = new TreeMap<>();
        try {
            METHOD_MAP.put("get", GetMethod.class.getConstructor(String.class));
            METHOD_MAP.put("put", PutMethod.class.getConstructor(String.class));
            METHOD_MAP.put("post", PostMethod.class.getConstructor(String.class));
            METHOD_MAP.put("delete", DeleteMethod.class.getConstructor(String.class));
            METHOD_MAP.put("options", OptionsMethod.class.getConstructor(String.class));
            METHOD_MAP.put("head", HeadMethod.class.getConstructor(String.class));
        } catch (NoSuchMethodException e) {
            // Should never happen
        }
    }

    /**
     * Create an httpMethod instance for the given method name
     * @param method The case-insensitive method name
     * @param url The url for the method
     * @return The method instance
     */
    public static HttpMethod createMethod(String method, String url) {
        Constructor<? extends HttpMethod> ctor = METHOD_MAP.get(method.toLowerCase());
        if( ctor == null ) {
            throw new IllegalArgumentException("Unknown method: " + method);
        }

        try {
            return ctor.newInstance(url);
        } catch( Exception e ) {
            // None of these should happen, but convert them to a runtime error
            throw new RuntimeException("Unable to construct method", e);
        }
    }

    /**
     * Returns a path with parameters substituted.
     * @param path The path (in format path/{Parameter}/etc)
     * @param params The parameters to substitute
     * @return The substituted path
     */
    public static String resolvePathParameters(String path, Object[] params) {
        // split path int
        String[] parts = path.split("((?<=/)|(?=/))");

        StringBuilder result = new StringBuilder();
        for( String part: parts ) {
            if( part.startsWith("{") && part.endsWith("}") ) {
                // Perform parameter replacement
                String param = part.substring(1, part.length() - 1);
                if( params == null ) {
                    throw new IllegalArgumentException("Missing parameter: " + param);
                }
                if( params.length % 2 == 1 ) {
                    throw new IllegalArgumentException("Unbalanced parameters!");
                }

                boolean matched = false;

                for( int i = 0; i < params.length && !matched; i += 2 ) {
                    String key = params[i].toString();
                    if( param.equals(key) ) {
                        result.append(params[i+1]);
                        matched = true;
                    }
                }

                if( !matched ) {
                    throw new IllegalArgumentException("Missing parameter: " + param);
                }
            } else {
                result.append(part);
            }
        }

        return result.toString();
    }

    /**
     * Resolves query parameters
     * @param defaultParameters A map of default params
     * @param parameters The additional parameters
     * @return The query string
     */
    public static String buildQueryString(Map<String, String> defaultParameters, Object[] parameters) {
        StringBuilder result = new StringBuilder();

        boolean first = true;

        try {
            // Default params
            for (String key : defaultParameters.keySet()) {
                if (first) {
                    result.append('?');
                    first = false;
                } else {
                    result.append('&');
                }
                result.append(URIUtil.encodeQuery(key));

                String value = defaultParameters.get(key);
                if (value != null) {
                    result.append('=');
                    result.append(URIUtil.encodeQuery(value));
                }
            }

            if( parameters != null ) {
                if( parameters.length % 2 == 1 ) {
                    throw new IllegalArgumentException("Query parameters are unbalanced!");
                }
                for( int i = 0; i < parameters.length; i += 2 ) {
                    if (first) {
                        result.append('?');
                        first = false;
                    } else {
                        result.append('&');
                    }
                    if( parameters[i] == null ) {
                        throw new IllegalArgumentException("Invalid query parameter (null)");
                    }
                    result.append(URIUtil.encodeQuery(parameters[i].toString()));

                    // If they specify null or the literal value true, don't add the equals
                    if( parameters[i+1] != null && !Boolean.TRUE.equals(parameters[i+1]) ) {
                        result.append('=');
                        result.append(URIUtil.encodeQuery(parameters[i+1].toString()));
                    }
                }
            }

        } catch( URIException e ) {
            throw new RuntimeException("Invalid query parameter value", e);
        }

        return result.toString();
    }

    /**
     * Add additional headers to method
     * @param method The method to update
     * @param headers The headers object
     */
    static void addMethodHeaders(HttpMethod method, Object[] headers) {
        if( headers == null || headers.length == 0 ) {
            return;
        }
        if( headers.length % 2 == 1 ) {
            throw new IllegalArgumentException("Unbalanced headers!");
        }

        for( int i = 0; i < headers.length; i += 2 ) {
            if( headers[i] == null || headers[i+1] == null ) {
                throw new IllegalArgumentException("Unexpected null header");
            }

            String name = headers[i].toString();
            String value = headers[i+1].toString();

            method.setRequestHeader(name, value);
        }
    }

    /**
     * Set the request entity with one of body, postParams, or files.
     * @param method The method to update
     * @param body The body
     * @param postParams The form post parameters
     * @param files The files
     */
    public static void setRequestEntity(HttpMethod method, String body, Object[] postParams, Object[] files)
            throws IOException
    {
        // Only set on put/post
        if( method instanceof EntityEnclosingMethod ) {
            EntityEnclosingMethod request = (EntityEnclosingMethod) method;

            if( body != null && !body.isEmpty() ) {
                // Start with body
                request.setRequestEntity(new StringRequestEntity(body, null, null));
            } else {
                if( postParams != null && postParams.length > 0 ) {
                    setRequestEntityFormData(request, postParams);
                }
                if( files != null & files.length > 0 ) {
                    setRequestEntityFiles(request, files);
                }
            }
        }
    }

    private static void setRequestEntityFormData(EntityEnclosingMethod method, Object[] postParams) {
        if( postParams.length % 2 == 1 ) {
            throw new IllegalArgumentException("Unbalanced post parameters!");
        }

        int count = postParams.length / 2;
        NameValuePair[] params = new NameValuePair[count];
        for( int i = 0; i < postParams.length; i+= 2 ) {
            if( postParams[i] == null || postParams[i+1] == null ) {
                throw new IllegalArgumentException("Unexpected null header");
            }

            String name = postParams[i].toString();
            String value = postParams[i+1].toString();

            params[i/2] = new NameValuePair(name, value);
        }

        String content = EncodingUtil.formUrlEncode(params, method.getRequestCharSet());
        method.setRequestEntity(new ByteArrayRequestEntity(EncodingUtil.getAsciiBytes(content),
                FORM_URL_ENCODED_CONTENT_TYPE));
    }

    private static void setRequestEntityFiles(EntityEnclosingMethod method, Object[] files) throws IOException {
        if (files.length % 3 == 1) {
            throw new IllegalArgumentException("Unbalanced files!");
        }

        PartBase[] parts = new PartBase[files.length / 3];
        for (int i = 0; i < files.length; i += 3) {
            if (files[i] == null || files[i + 1] == null) {
                throw new IllegalArgumentException("Unexpected null file");
            }

            String name = files[i].toString();
            if( name.equals("file:") ) {
                name = "";
            }

            // If it's a string type, check if the file exists, otherwise add a string part
            if (files[i + 1] instanceof String) {
                String data = (String) files[i + 1];
                File file = new File(data);
                if (file.isFile()) {
                    // Add a file part
                    if( name.isEmpty() ) {
                        name = file.getName();
                    }
                    parts[i / 3] = new FilePart(name, file);
                } else {
                    // Add a string part
                    if( name.isEmpty() ) {
                        throw new IllegalArgumentException("File name is required!");
                    }
                    parts[i / 3] = new StringPart(name, data);
                }
            } else if (files[i + 1] instanceof byte[]) {
                parts[i / 3] = new FilePart(name, new ByteArrayPartSource(name, (byte[]) files[i + 1]));
            } else {
                // TODO: Convert to byte array if it's a numeric array?
                throw new IllegalArgumentException("Unexpected file data type: " +
                        files[i + 1].getClass().getCanonicalName());
            }

            String contentType = (String)files[i+2];
            if( contentType == null || contentType.isEmpty() ) {
                contentType = guessFileType(name);
            }
            parts[i / 3].setContentType(contentType);
        }

        method.setRequestEntity(new MultipartRequestEntity(parts, method.getParams()));
    }

    public static String guessFileType(String name) {
        String result = null;
        if( FILE_NAME_MAP != null ) {
            result = FILE_NAME_MAP.getContentTypeFor(name);
        }
        if( result == null || result.isEmpty() ) {
            result = DEFAULT_FILE_TYPE;
        }
        return result;
    }

    // Hooray java generics!
    public static short[] convertByteArrayToShort(byte[] src) {
        short[] dst = new short[src.length];
        for( int i = 0; i < src.length; i++ ) {
            dst[i] = (short)(src[i] & 0xFF);
        }
        return dst;
    }

    public static int[] convertByteArrayToInt(byte[] src) {
        int[] dst = new int[src.length];
        for( int i = 0; i < src.length; i++ ) {
            dst[i] = src[i] & 0xFF;
        }
        return dst;
    }

    public static long[] convertByteArrayToLong(byte[] src) {
        long[] dst = new long[src.length];
        for( int i = 0; i < src.length; i++ ) {
            dst[i] = (long)(src[i] & 0xFF);
        }
        return dst;
    }

    public static double[] convertByteArrayToDouble(byte[] src) {
        double[] dst = new double[src.length];
        for( int i = 0; i < src.length; i++ ) {
            dst[i] = (double)(src[i] & 0xFF);
        }
        return dst;
    }

    public static char[] convertByteArrayToChar(byte[] src) {
        char[] dst = new char[src.length];
        for( int i = 0; i < src.length; i++ ) {
            dst[i] = (char)(src[i] & 0xFF);
        }
        return dst;
    }
}
