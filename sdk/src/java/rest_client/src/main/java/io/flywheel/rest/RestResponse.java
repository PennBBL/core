package io.flywheel.rest;

import java.io.IOException;

/**
 * Interface for querying response data
 */
public interface RestResponse {

    /**
     * Gets the http status code
     * @return The status code, or 0 if the request wasn't completed successfully
     */
    int getStatusCode();

    /**
     * Gets the http reason phrase
     * @return The http reason phrase, or null if the request wasn't completed successfully
     */
    String getReasonPhrase();

    /**
     * Gets the http response body as a string
     * @return The response body as a string, or empty string if there is no response.
     */
    String getBodyAsString() throws IOException;

    /**
     * Gets the http response body in the given format. Conversion will be done from
     * uint8 bytes to output format
     * @param format The format, one of 'int8', 'int16', 'int32', 'int64', 'double' or 'char'
     */
    Object getBodyData(String format) throws IOException;

    /**
     * Saves the http response body to the given path.
     * @param path The path to save the response body at
     */
    void saveResponseBodyToFile(String path) throws IOException;

    /**
     * Get all of the headers that match name
     * @param name The case-insensitive name of headers to retrieve
     * @return The set of headers that match name
     */
    String[] getHeaders(String name);

    /**
     * Get the first header that matches name
     * @param name The case-insensitive name of the header to retrieve
     * @return The value of the first instance of the header name, or null if not found
     */
    String getFirstHeader(String name);

    /**
     * Get the names of all of the headers on the response
     * @return An array of all response headers
     */
    String[] getAllHeaderNames();

    /**
     * Get the full URL of the original request.
     * @return A string containing the request url
     */
    String getRequestUrl();
}
