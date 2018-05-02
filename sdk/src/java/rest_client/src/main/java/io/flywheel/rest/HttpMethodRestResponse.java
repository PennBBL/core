package io.flywheel.rest;

import org.apache.commons.httpclient.Header;
import org.apache.commons.httpclient.HttpMethod;

import java.io.*;
import java.util.ArrayList;

/**
 * HttpClient 3.1 implementation of RestResponse
 * @class HttpMethodRestResponse
 */
public class HttpMethodRestResponse implements RestResponse {

    private static final String[] EMPTY_STRING_ARRAY = {};

    private final String url;
    private final HttpMethod method;

    /**
     * Construct a RestResponse from HttpMethod
     * @param url The requested url
     * @param method The http method, must not be null.
     */
    public HttpMethodRestResponse(final String url, final HttpMethod method) {
        this.url = url;
        this.method = method;

        if( this.method == null ) {
            throw new IllegalArgumentException("HttpMethod cannot be null!");
        }
    }

    @Override
    public int getStatusCode() {
        return method.getStatusCode();
    }

    @Override
    public String getReasonPhrase() {
        return method.getStatusText();
    }

    @Override
    public String getBodyAsString() throws IOException {
        return method.getResponseBodyAsString();
    }

    @Override
    public Object getBodyData(String format) throws IOException {
        byte[] data = method.getResponseBody();

        if( format.equals("int8") ) {
            return data;
        } else if( format.equals("int16") ) {
            return RestUtils.convertByteArrayToShort(data);
        } else if( format.equals("int32") ) {
            return RestUtils.convertByteArrayToInt(data);
        } else if( format.equals("int64") ) {
            return RestUtils.convertByteArrayToLong(data);
        } else if( format.equals("double") ) {
            return RestUtils.convertByteArrayToDouble(data);
        } else if( format.equals("char") ) {
            return RestUtils.convertByteArrayToChar(data);
        }

        throw new IllegalArgumentException("Unknown body format: " + format);
    }

    @Override
    public void saveResponseBodyToFile(String path) throws IOException {
        InputStream in = null;
        OutputStream out = null;
        byte[] buffer = new byte[8192];

        try {
            in = method.getResponseBodyAsStream();
            out = new FileOutputStream(path);

            int len = in.read(buffer);
            while( len != -1 ) {
                if( len > 0 ) {
                    out.write(buffer, 0, len);
                }
                len = in.read(buffer);
            }
        } finally {
            safeClose(in);
            safeClose(out);
        }
    }

    @Override
    public String[] getHeaders(String name) {
        Header[] headers = method.getResponseHeaders(name);

        if( headers == null ) {
            return EMPTY_STRING_ARRAY;
        }


        String[] result = new String[headers.length];
        for( int i = 0; i < headers.length; i++ ) {
            result[i] = headers[i].getValue();
        }
        return result;
    }

    @Override
    public String getFirstHeader(String name) {
        Header result = method.getResponseHeader(name);
        if( result == null ) {
            return null;
        }
        return result.getValue();
    }

    @Override
    public String[] getAllHeaderNames() {
        Header[] headers = method.getResponseHeaders();
        if( headers == null ) {
            return EMPTY_STRING_ARRAY;
        }
        String[] result = new String[headers.length];
        for( int i = 0; i < headers.length; i++ ) {
            result[i] = headers[i].getName();
        }
        return result;
    }

    @Override
    public String getRequestUrl() {
        return url;
    }

    private static void safeClose(Closeable c) {
        if( c != null ) {
            try {
                c.close();
            } catch( Exception e ) {}
        }
    }
}
