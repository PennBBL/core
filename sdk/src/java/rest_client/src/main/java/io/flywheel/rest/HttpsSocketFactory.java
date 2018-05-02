package io.flywheel.rest;

import org.apache.commons.httpclient.ConnectTimeoutException;
import org.apache.commons.httpclient.params.HttpConnectionParams;
import org.apache.commons.httpclient.protocol.Protocol;
import org.apache.commons.httpclient.protocol.ProtocolSocketFactory;

import javax.net.ssl.*;
import java.io.IOException;
import java.io.InputStream;
import java.net.*;
import java.security.KeyStore;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Custom Socket factory to create SSL Sockets that support modern protocols, algorithms, and certificates.
 * This class assumes an older JVM (such as the JVM bundled with Matlab).
 * This is dependent on Apache HttpClient 3.x being present in the classpath.
 *
 * The cacerts used by this class is bundled from the build environment at build time. This was the lowest
 * barrier to getting a modern set of certificates into the Matlab JVM. Without this, there may be security
 * implications (e.g. using revoked CAs) and we would not be able to connect to our development systems
 * where LetsEncrypt is used.
 */
public class HttpsSocketFactory implements ProtocolSocketFactory {

    private final String[] enabledProtocols;
    private final String[] enabledCipherSuites;
    private final SSLContext sslContext;

    // Secure set of protocols and cipher suites to support
    // See https://docs.oracle.com/javase/7/docs/technotes/guides/security/SunProviders.html for the list of suites
    // provided by Java.
    // See also: https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices
    // The below list is the supported subset of the lists in the above articles
    private static final String[] DEFAULT_PROTOCOLS = {"TLSv1.2", "TLSv1.1"};
    private static final String[] DESIRED_CIPHER_SUITES = {
            "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
            "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
            "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
            "TLS_DHE_DSS_WITH_AES_256_GCM_SHA384",
            "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            "TLS_DHE_DSS_WITH_AES_128_GCM_SHA256",
            "TLS_DHE_DSS_WITH_AES_256_CBC_SHA256",
            "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
            "TLS_RSA_WITH_AES_256_CBC_SHA256",
            "TLS_RSA_WITH_AES_128_CBC_SHA256"
    };

    /**
     * Safely create a keystore using the bundled cacerts.
     * @return The created keystore
     */
    private KeyStore createKeystore() {
        InputStream in = null;
        try {
            in = getClass().getResourceAsStream("/io/flywheel/rest/cacerts");
            KeyStore ks = KeyStore.getInstance("JKS");
            ks.load(in, null);
            return ks;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        } finally {
            try {
                in.close();
            } catch( Exception e ) {}
        }
    }

    /**
     * Safely create and return an SSL context that validates certificates using the
     * bundled CA certs.
     * @return The created context
     */
    private SSLContext createSSLContext() {
        try {
            KeyStore ks = createKeystore();
            if( ks == null ) {
                return null;
            }

            TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
            tmf.init(ks);

            SSLContext context = SSLContext.getInstance("TLS");
            context.init(null, tmf.getTrustManagers(), null);

            return context;
        } catch(Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Construct an HttpSocketFactory from a base factory, enabling the given protocols
     * @param enabledProtocols The list of enabled protocols
     */
    private HttpsSocketFactory(String[] enabledProtocols) {
        try {
            this.sslContext = createSSLContext();
        } catch( Exception e ) {
            throw new RuntimeException("Unable to create ssl context", e);
        }

        this.enabledProtocols = enabledProtocols;
        this.enabledCipherSuites = determineEnabledCipherSuites();
    }

    /**
     * Create a socket that is bound to localAddress:localPort and connects to host:port
     * {@inheritDoc}
     */
    @Override
    public Socket createSocket(String host, int port, InetAddress localAddress, int localPort)
            throws IOException, UnknownHostException
    {
        Socket result = sslContext.getSocketFactory().createSocket(host, port, localAddress, localPort);
        return setProtocols(result);
    }

    /**
     * Create a socket that is bound to localAddress:localPort and connects to host:port, with an optional
     * timeout specified via httpConnection params
     * {@inheritDoc}
     */
    @Override
    public Socket createSocket(String host, int port, InetAddress localAddress, int localPort,
                               HttpConnectionParams httpConnectionParams)
            throws IOException, UnknownHostException, ConnectTimeoutException
    {
        if( httpConnectionParams == null ) {
            throw new IllegalArgumentException("Parameters may not be null");
        }

        int timeout = httpConnectionParams.getConnectionTimeout();
        Socket result;

        if( timeout == 0 ) {
            result = sslContext.getSocketFactory().createSocket(host, port, localAddress, localPort);
            setProtocols(result);
        } else {
            result = sslContext.getSocketFactory().createSocket();
            SocketAddress localaddr = new InetSocketAddress(localAddress, localPort);
            SocketAddress remoteaddr = new InetSocketAddress(host, port);
            setProtocols(result);
            result.bind(localaddr);
            result.connect(remoteaddr, timeout);
        }

        return result;
    }

    /**
     * Create a socket that connects to host:port
     * {@inheritDoc}
     */
    @Override
    public Socket createSocket(String host, int port) throws IOException, UnknownHostException {
        Socket result = sslContext.getSocketFactory().createSocket(host, port);
        return setProtocols(result);
    }

    /**
     * Set the list of enabled protocols on socket and cipher suites on socket
     * @param socket The socket to configure
     * @return The socket
     */
    private Socket setProtocols(Socket socket) {
        if( socket instanceof SSLSocket ) {
            SSLSocket sslSocket = (SSLSocket)socket;
            sslSocket.setEnabledProtocols(enabledProtocols);
            if( enabledCipherSuites != null && enabledCipherSuites.length > 0 ) {
                sslSocket.setEnabledCipherSuites(enabledCipherSuites);
            }
        }
        return socket;
    }

    /**
     * Register this factory as the https handler for HttpClient
     */
    public static void register() {
        Protocol baseProtocol = Protocol.getProtocol("https");
        int defaultPort = baseProtocol.getDefaultPort();

        Protocol customProtocol = new Protocol("https", new HttpsSocketFactory(DEFAULT_PROTOCOLS), defaultPort);
        Protocol.registerProtocol("https", customProtocol);
    }

    /**
     * Determine the list of enabled cipher suites from the desired list.
     * @return The list of cipher suites that can be used.
     */
    public static String[] determineEnabledCipherSuites() {
        ArrayList<String> result = new ArrayList<>();
        try {
            SSLSocket sock = (SSLSocket)SSLSocketFactory.getDefault().createSocket();

            // Add desired suites first
            List<String> supportedSuites = Arrays.asList(sock.getSupportedCipherSuites());
            for( String suite : DESIRED_CIPHER_SUITES ) {
                if( supportedSuites.contains(suite) ) {
                    result.add(suite);
                }
            }

            // Add remaining suites
            String[] enabledSuites = sock.getEnabledCipherSuites();
            for( String suite : enabledSuites ) {
                result.add(suite);
            }
        } catch( Exception e ) {
            e.printStackTrace();
        }

        return result.toArray(new String[result.size()]);
    }
}
