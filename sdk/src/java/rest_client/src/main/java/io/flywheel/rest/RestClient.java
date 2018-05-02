package io.flywheel.rest;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.EntityEnclosingMethod;
import org.apache.commons.httpclient.methods.StringRequestEntity;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;
import java.util.TreeMap;

/**
 * @class RestClient
 * Provides Rest services for the Matlab SDK
 */
public class RestClient {

    private HttpClient client;
    private URL baseUrl;
    private Map<String, String> defaultHeaders = new TreeMap<>();
    private Map<String, String> defaultParameters = new TreeMap<>();

    private static final String JSON_CONTENT_TYPE = "application/json";

    /**
     * Constructs a RestClient with the provided baseUrl
     * @param baseUrl The baseUrl. All requests will be relative to this URL.
     */
    public RestClient(URL baseUrl) {
        this(baseUrl, null);
    }

    /**
     * Constructs a RestClient with the provided baseUrl and API key
     * @param baseUrl The baseUrl. All requests will be relative to this URL.
     * @param apiKey The api key to use for authorization
     */
    public RestClient(URL baseUrl, String apiKey) {
        // Perform one-time initializations
        HttpClientInit.initialize();

        // Split API Key...
        // Set default header
        this.baseUrl = baseUrl;

        this.client = new HttpClient();

        if( apiKey != null && !apiKey.isEmpty() ) {
            defaultHeaders.put("Authorization", "scitran-user " + apiKey);
        }
    }

    /**
     * Construct a RestClient from an API key
     * @param apiKey The api key, in the form of host:[port:][...:]key
     * @return The newly constructed rest client
     * @throws MalformedURLException
     */
    public static RestClient fromApiKey(String apiKey) throws MalformedURLException {
        String host = "";
        String key = "";
        int port = 443;

        // Parse host, port, and key from API key
        String[] parts = apiKey.split(":");
        if( parts.length < 2 ) {
            throw new IllegalArgumentException("Invalid API key");
        }

        host = parts[0];

        if( parts.length == 2 ) {
            key = parts[1];
        } else {
            port = Integer.parseInt(parts[1]);
            key = parts[parts.length-1];
        }

        return new RestClient(new URL("https", host, port, "/api/"), key);
    }

    /**
     * Performs the provided method against path, with a content type of application/json.
     * @param method The method to perform (case insensitive). Supported methods are:
     *               get, put, post, delete, options
     * @param path The path of the request
     * @param body The request body, if applicable
     * @return
     */
    public RestResponse performJson(String method, String path, String body) throws IOException {
        if( path.startsWith("/") ) {
            path = path.substring(1);
        }

        String url = new URL(this.baseUrl, path).toString();

        HttpMethod request = RestUtils.createMethod(method, url);
        initializeMethod(request, JSON_CONTENT_TYPE, body);

        client.executeMethod(request);

        return new HttpMethodRestResponse(url, request);
    }

    /**
     * Performs the provided method against path, with a content type of application/json.
     * @param method The method to perform (case insensitive). Supported methods are:
     *               get, put, post, delete, options
     * @param path The path of the request
     * @return
     */
    public RestResponse performJson(String method, String path) throws IOException {
        return performJson(method, path, null);
    }

    /**
     * Performs an api call with the provided settings.
     * @param method The HTTP method (e.g. GET)
     * @param path The resource path, relative to baseUrl
     * @param pathParams The path parameters as pairs of [name, value]
     * @param queryParams The query parameters as pairs of [name, value]
     * @param headers The headers as pairs of [name, value]
     * @param body The request body
     * @param postParams Post parameters as pairs of [name, value]
     * @param files Files as pairs of [filename, filepath or data]
     * @return The response object
     */
    public RestResponse callApi(String method, String path, Object[] pathParams,
                                Object[] queryParams, Object[] headers, String body, Object[] postParams,
                                Object[] files) throws IOException
    {
        // Resolve the path
        path = RestUtils.resolvePathParameters(path, pathParams);

        if( path.startsWith("/") ) {
            path = path.substring(1);
        }

        // Resolve query parameters
        String query = RestUtils.buildQueryString(defaultParameters, queryParams);

        // Resolve url with query parameters
        String url = new URL(this.baseUrl, path).toString() + query;

        // Create the request with default headers
        HttpMethod request = RestUtils.createMethod(method, url);

        setDefaultHeaders(request);

        // Add additional headers
        RestUtils.addMethodHeaders(request, headers);

        // Set the request entity based on provided body, postParams, and files
        RestUtils.setRequestEntity(request, body, postParams, files);

        client.executeMethod(request);

        return new HttpMethodRestResponse(url, request);
    }

    /**
     * Add a query parameter to be set on every request.
     * @param name The parameter name
     * @param value The parameter value
     */
    public void addDefaultParameter(String name, String value) {
        defaultParameters.put(name, value);
    }

    /**
     * Add a header to be set on every request.
     * @param name The header name
     * @param value The header value
     */
    public void setDefaultHeader(String name, String value) {
        defaultHeaders.put(name, value);
    }

    /**
     * Initializes method with the default headers, including authorization, and
     * sets the request entity, if a body is specified.
     * @param method The method instance
     * @param contentType The content type of the body
     * @param body The body contents
     */
    private void initializeMethod(HttpMethod method, String contentType, String body) {
        // Add default headers
        setDefaultHeaders(method);

        if( body != null ) {
            EntityEnclosingMethod request;

            try {
                request = (EntityEnclosingMethod) method;
            } catch( ClassCastException e ) {
                throw new RuntimeException("Specifying a request body is not supported for: " + method.getName());
            }

            try {
                request.setRequestEntity(new StringRequestEntity(body, contentType, null));
            } catch( UnsupportedEncodingException e ) {
                // Shouldn't happen?
                throw new RuntimeException("Unsupported encoding");
            }
        }
    }

    private void setDefaultHeaders(HttpMethod method) {
        for( String headerKey: defaultHeaders.keySet() ) {
            method.setRequestHeader(headerKey, defaultHeaders.get(headerKey));
        }
    }

}
