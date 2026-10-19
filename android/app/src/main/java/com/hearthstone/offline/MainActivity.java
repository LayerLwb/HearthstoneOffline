package com.hearthstone.offline;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.graphics.Color;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.JavascriptInterface;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLDecoder;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public class MainActivity extends Activity {
    private static final String TAG = "HSO_Main";
    private static final int PERMISSION_REQUEST_CODE = 2026;
    private static final Map<String, String> MIME_TYPES = new HashMap<>();
    private static SSLSocketFactory sslSocketFactory;
    private static HostnameVerifier hostnameVerifier;

    // HSO.zip 外部美术资源包管理
    private static volatile ZipFile hsoZipFile = null;
    private static volatile String hsoZipPath = null;
    private static boolean hasPromptedMissing = false;

    private WebView webView;

    static {
        MIME_TYPES.put("html", "text/html");
        MIME_TYPES.put("htm", "text/html");
        MIME_TYPES.put("js", "application/javascript");
        MIME_TYPES.put("mjs", "application/javascript");
        MIME_TYPES.put("css", "text/css");
        MIME_TYPES.put("json", "application/json");
        MIME_TYPES.put("jsonl", "application/json");
        MIME_TYPES.put("webp", "image/webp");
        MIME_TYPES.put("png", "image/png");
        MIME_TYPES.put("jpg", "image/jpeg");
        MIME_TYPES.put("jpeg", "image/jpeg");
        MIME_TYPES.put("gif", "image/gif");
        MIME_TYPES.put("svg", "image/svg+xml");
        MIME_TYPES.put("woff", "font/woff");
        MIME_TYPES.put("woff2", "font/woff2");
        MIME_TYPES.put("ttf", "font/ttf");
        MIME_TYPES.put("otf", "font/otf");
        MIME_TYPES.put("mp3", "audio/mpeg");
        MIME_TYPES.put("ogg", "audio/ogg");
        MIME_TYPES.put("wav", "audio/wav");
        MIME_TYPES.put("wasm", "application/wasm");
    }

    private static synchronized void initSsl() {
        if (sslSocketFactory != null) return;
        try {
            TrustManager[] trustAllCerts = new TrustManager[]{
                new X509TrustManager() {
                    @Override
                    public void checkClientTrusted(X509Certificate[] chain, String authType) {}

                    @Override
                    public void checkServerTrusted(X509Certificate[] chain, String authType) {}

                    @Override
                    public X509Certificate[] getAcceptedIssuers() {
                        return new X509Certificate[0];
                    }
                }
            };
            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(null, trustAllCerts, new SecureRandom());
            sslSocketFactory = sslContext.getSocketFactory();
            hostnameVerifier = new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            };
        } catch (Exception ignored) {}
    }

    static HttpURLConnection openSecureConnection(String urlString) throws Exception {
        initSsl();
        URL url = new URL(urlString);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        if (conn instanceof HttpsURLConnection) {
            HttpsURLConnection httpsConn = (HttpsURLConnection) conn;
            if (sslSocketFactory != null) {
                httpsConn.setSSLSocketFactory(sslSocketFactory);
            }
            if (hostnameVerifier != null) {
                httpsConn.setHostnameVerifier(hostnameVerifier);
            }
        }
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(15000);
        conn.setReadTimeout(20000);
        conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36");
        return conn;
    }

    /**
     * 自动在手机中检索并打开 HSO.zip 美术资源包
     * 优先搜索 Download 目录，兼顾多种设备存储路径与免权限私有目录
     */
    public static synchronized boolean initHsoZip(Context context) {
        if (hsoZipFile != null) {
            return true;
        }

        List<File> searchDirs = new ArrayList<>();

        // 1. 系统标准 Download 目录
        try {
            File downloads = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
            if (downloads != null) searchDirs.add(downloads);
        } catch (Exception ignored) {}

        // 2. 常见手机厂商外部存储路径
        searchDirs.add(new File("/storage/emulated/0/Download"));
        searchDirs.add(new File("/sdcard/Download"));
        searchDirs.add(new File("/storage/emulated/0/Downloads"));
        searchDirs.add(new File("/sdcard/Downloads"));

        // 3. 应用外部私有目录（免任何权限直接可读）
        if (context != null) {
            try {
                File extFiles = context.getExternalFilesDir(null);
                if (extFiles != null) {
                    searchDirs.add(extFiles);
                    searchDirs.add(new File(extFiles, "Download"));
                }
            } catch (Exception ignored) {}
        }

        // 4. 根存储目录及子目录
        try {
            File extStorage = Environment.getExternalStorageDirectory();
            if (extStorage != null) {
                searchDirs.add(new File(extStorage, "Download"));
                searchDirs.add(new File(extStorage, "Downloads"));
                searchDirs.add(extStorage);
            }
        } catch (Exception ignored) {}

        searchDirs.add(new File("/storage/emulated/0"));
        searchDirs.add(new File("/sdcard"));

        for (File dir : searchDirs) {
            if (dir == null || !dir.exists() || !dir.isDirectory()) continue;
            for (String name : new String[]{"HSO.zip", "hso.zip"}) {
                File candidate = new File(dir, name);
                if (candidate.exists() && candidate.isFile() && candidate.canRead()) {
                    try {
                        ZipFile zf = new ZipFile(candidate);
                        if (zf.size() > 0) {
                            hsoZipFile = zf;
                            hsoZipPath = candidate.getAbsolutePath();
                            Log.i(TAG, "已成功挂载外部美术资源包: " + hsoZipPath + " (条目数: " + zf.size() + ")");
                            return true;
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "尝试挂载美术包失败: " + candidate.getAbsolutePath(), e);
                    }
                }
            }
        }
        return false;
    }

    public static class AndroidBridge {
        private final Context context;

        public AndroidBridge(Context context) {
            this.context = context;
        }

        @JavascriptInterface
        public String fetchUrl(String url) {
            HttpURLConnection conn = null;
            try {
                conn = openSecureConnection(url);
                int code = conn.getResponseCode();
                if (code >= 200 && code < 300) {
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        sb.append(line);
                    }
                    reader.close();
                    return sb.toString();
                }
            } catch (Exception ignored) {
            } finally {
                if (conn != null) {
                    try {
                        conn.disconnect();
                    } catch (Exception ignored) {}
                }
            }
            return null;
        }

        @JavascriptInterface
        public boolean hasHsoZip() {
            return hsoZipFile != null || initHsoZip(context);
        }

        @JavascriptInterface
        public String getHsoZipPath() {
            return hsoZipPath != null ? hsoZipPath : "";
        }

        @JavascriptInterface
        public String checkHsoStatus() {
            boolean loaded = hasHsoZip();
            return "{\"loaded\":" + loaded + ",\"path\":\"" + (hsoZipPath != null ? hsoZipPath.replace("\\", "\\\\") : "") + "\"}";
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            WindowManager.LayoutParams lp = getWindow().getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            getWindow().setAttributes(lp);
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            getWindow().setDecorFitsSystemWindows(false);
        }

        hideSystemUI();

        // 检查并请求存储读取权限
        checkAndRequestStoragePermissions();

        // 尝试自动加载 Download/HSO.zip 美术包
        boolean zipFound = initHsoZip(this);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.parseColor("#21140e"));
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);

        webView.addJavascriptInterface(new AndroidBridge(this), "androidBridge");

        final AssetManager assetManager = getAssets();

        // 提示用户美术包状态
        if (zipFound) {
            Toast.makeText(this, "🎨 已成功加载美术资源包: " + hsoZipPath, Toast.LENGTH_SHORT).show();
        } else {
            // 检查 APK 内部是否已内置原画
            boolean hasBuiltInArt = false;
            try {
                String[] list = assetManager.list("art");
                if (list != null && list.length > 50) {
                    hasBuiltInArt = true;
                }
            } catch (Exception ignored) {}

            if (!hasBuiltInArt && !hasPromptedMissing) {
                hasPromptedMissing = true;
                Toast.makeText(this, "💡 提示：未检测到 Download/HSO.zip 美术包。请将 HSO.zip 放置在手机 Download 目录下以加载完整卡牌原画。", Toast.LENGTH_LONG).show();
            }
        }

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage consoleMessage) {
                Log.d("HSO_WebView", consoleMessage.message() + " [" + consoleMessage.sourceId() + ":" + consoleMessage.lineNumber() + "]");
                return true;
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                handler.proceed();
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (request == null || request.getUrl() == null) {
                    return null;
                }
                return handleResourceIntercept(request.getUrl());
            }

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
                if (url == null || url.isEmpty()) {
                    return null;
                }
                return handleResourceIntercept(Uri.parse(url));
            }

            private WebResourceResponse handleResourceIntercept(Uri uri) {
                String host = uri.getHost();
                if (host != null && !host.equalsIgnoreCase("localhost") && !host.equals("127.0.0.1")) {
                    return null;
                }

                String path = uri.getPath();
                if (path != null && path.startsWith("/api/proxy")) {
                    String targetUrl = uri.getQueryParameter("url");
                    if (targetUrl != null && !targetUrl.isEmpty()) {
                        try {
                            HttpURLConnection conn = openSecureConnection(targetUrl);
                            int statusCode = conn.getResponseCode();
                            String contentType = conn.getContentType();
                            String mime = "application/json";
                            if (contentType != null && !contentType.isEmpty()) {
                                int semi = contentType.indexOf(';');
                                mime = (semi != -1 ? contentType.substring(0, semi) : contentType).trim();
                            }
                            Map<String, String> headers = new HashMap<>();
                            headers.put("Access-Control-Allow-Origin", "*");
                            headers.put("Access-Control-Allow-Methods", "GET, OPTIONS");
                            return new WebResourceResponse(mime, "UTF-8", statusCode, "OK", headers, conn.getInputStream());
                        } catch (Exception e) {
                            return new WebResourceResponse("text/plain", "UTF-8", 500, "Proxy Error: " + e.getMessage(), null, null);
                        }
                    }
                }

                if (path == null || path.isEmpty() || path.equals("/")) {
                    path = "index.html";
                } else if (path.startsWith("/")) {
                    path = path.substring(1);
                }

                String decodedPath = "";
                try {
                    decodedPath = URLDecoder.decode(path, "UTF-8");
                } catch (Exception ignored) {
                    decodedPath = path;
                }

                InputStream is = null;

                // 1. 优先尝试从 APK 内置 assets 读取
                try {
                    is = assetManager.open(decodedPath);
                } catch (Exception ignored) {}

                // 2. 若内置 assets 无此文件，则自动尝试从手机 Download 目录的 HSO.zip 读取美术等资源
                if (is == null) {
                    if (hsoZipFile == null) {
                        initHsoZip(MainActivity.this);
                    }
                    if (hsoZipFile != null) {
                        try {
                            ZipEntry entry = hsoZipFile.getEntry(decodedPath);
                            if (entry == null && !decodedPath.startsWith("assets/")) {
                                entry = hsoZipFile.getEntry("assets/" + decodedPath);
                            }
                            if (entry == null && decodedPath.startsWith("assets/")) {
                                entry = hsoZipFile.getEntry(decodedPath.substring(7));
                            }
                            if (entry == null) {
                                int slash = decodedPath.indexOf('/');
                                if (slash != -1) {
                                    entry = hsoZipFile.getEntry(decodedPath.substring(slash + 1));
                                }
                            }
                            if (entry != null) {
                                is = hsoZipFile.getInputStream(entry);
                            }
                        } catch (Exception e) {
                            Log.e(TAG, "从 HSO.zip 读取条目异常: " + decodedPath, e);
                        }
                    }
                }

                if (is != null) {
                    String ext = "";
                    int lastDot = decodedPath.lastIndexOf('.');
                    if (lastDot != -1) {
                        ext = decodedPath.substring(lastDot + 1).toLowerCase();
                    }
                    String mimeType = MIME_TYPES.get(ext);
                    if (mimeType == null) {
                        mimeType = "application/octet-stream";
                    }

                    // 关键修复：图片、音频、字体与二进制文件不能指定 UTF-8 编码，必须设为 null
                    String encoding = "UTF-8";
                    if (mimeType.startsWith("image/") || mimeType.startsWith("font/") || mimeType.startsWith("audio/") || mimeType.equals("application/wasm") || mimeType.equals("application/octet-stream")) {
                        encoding = null;
                    }

                    Map<String, String> responseHeaders = new HashMap<>();
                    responseHeaders.put("Access-Control-Allow-Origin", "*");
                    responseHeaders.put("Cache-Control", "public, max-age=604800");
                    return new WebResourceResponse(mimeType, encoding, 200, "OK", responseHeaders, is);
                }

                return null;
            }
        });

        webView.loadUrl("http://localhost/index.html");
    }

    private void checkAndRequestStoragePermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE
                }, PERMISSION_REQUEST_CODE);
            }
        }

        // Android 11+ (API 30+) 若未开启所有文件管理权限且无法直接读取 Download/HSO.zip，则指引用户开启
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                File dl = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                File candidate = new File(dl, "HSO.zip");
                if (candidate.exists() && !candidate.canRead()) {
                    try {
                        Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                        intent.setData(Uri.parse("package:" + getPackageName()));
                        startActivity(intent);
                        Toast.makeText(this, "请授予文件管理权限以读取 Download/HSO.zip 美术资源包", Toast.LENGTH_LONG).show();
                    } catch (Exception e) {
                        try {
                            Intent intent = new Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                            startActivity(intent);
                        } catch (Exception ignored) {}
                    }
                }
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (hsoZipFile == null) {
            if (initHsoZip(this)) {
                Toast.makeText(this, "🎨 已成功加载美术资源包: " + hsoZipPath, Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                if (initHsoZip(this)) {
                    Toast.makeText(this, "🎨 已成功加载美术资源包: " + hsoZipPath, Toast.LENGTH_SHORT).show();
                }
            }
        }
    }

    private void hideSystemUI() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        );
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUI();
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
