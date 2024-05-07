<?php

$_garlic_found_nonces = explode("\n", file_get_contents("/fuzzer/valid_nonces.txt"));

/* Here, we explicitely want this handler to fire when using the @ operator - but just not
 * to pollute the stdout. */
function handler($errno, $errstr, $errfile, $errline, $errcontext) {
    fwrite(STDERR, $errstr);
    return false;
}

set_error_handler("handler");


$payloads = array(
    "legitimateGARLIC",
    # The following two payloads are repeated on purpose to increase
    # the number of times thy are injected
    "</GARLIC'\"`>",
    "GARLIC GARLIC'\"`",
    "</GARLIC'\"`>",
    "GARLIC GARLIC'\"`",
    "GARLIC GARLIC\\",
    "false",
    "0",
    "1",
    "2",
    "3",
    "99",  # nonexistent id
    "invalidfolderGARLIC/filenameGARLIC",
    "http://GARLICGARLICGARLIC.example.com",
    'O:21:"GARLICNonexistentClass":0:{}',
    "legitimate.emailGARLIC@example.com",
    # this is a hack - true compares as equal to (most) nonempty strings, so it
    # allows us to discover some more behavior in the form of if ($_GET['...'] == '...'),
    # regardless of the hacked equality in the php source code.
    true
);


function add_magic_quotes_to_payload($array) {
    /* WordPress escapes the GET, POST etc. arrays as for compatibility reasons:
     * https://core.trac.wordpress.org/ticket/18322
     * We want to emulate that behavior so that we don't cause false positives (e.g.
     * bugs depending on these variables being not escaped).
     */
    if (is_array($array)) {
        foreach($array as $k => $v) {
            $array[$k] = add_magic_quotes_to_payload($v);
        }
        return $array;
    } elseif (is_string($array)) {
        return addslashes($array);
    } else {
        return $array;
    }
}


class MagicPayloadDictionary implements JsonSerializable {
    function __construct(
            $name,
            $escape,
            $prefix='',
            $original=array(),
            $ignore_wordpress_query_variables=false,
            $ignore_http_host=false) {
        $this->_garlic_name = $name;
        $this->_garlic_escape = $escape;
        $this->prefix = $prefix;
        $this->parameters = array();
        $this->original = $original;
        $this->ignore_wordpress_query_variables = $ignore_wordpress_query_variables;
        $this->ignore_http_host = $ignore_http_host;
    }

    function jsonSerialize() {
        return "(recursively returning magic object)";
    }

    function getAndSaveForFurtherGets($key) {
        if (array_key_exists($key, $this->original)) {
            return $this->original[$key];
        }

        if (array_key_exists($key, $this->parameters)) {
            return $this->parameters[$key];
        }

        if ($key == "REQUEST_METHOD") {
            $methods = [
                # GET and POST should be more frequent
                'GET', 'GET', 'GET',
                'POST', 'POST', 'POST',
                'PUT', 'DELETE', 'OPTIONS'];

            $method = $methods[array_rand($methods)];

            $this->parameters[$key] = $method;
            return $method;
        }

        if ($this->prefix !== '' && strpos($key, $this->prefix) !== 0) {
            return null;
        }

        switch (getenv('INTERCEPT_PROB')) {
            case '100':
                break;
            case '50':
                if (rand() % 2 == 0) {
                    $this->parameters[$key] = null;
                    return null;
                }
                break;
            case '33':
                if (rand() % 3 > 0) {
                    $this->parameters[$key] = null;
                    return null;
                }
                break;
            case '25':
                if (rand() % 4 > 0) {
                    $this->parameters[$key] = null;
                    return null;
                }
                break;
            case '10':
                if (rand() % 10 > 0) {
                    $this->parameters[$key] = null;
                    return null;
                }
                break;
            default:
                $this->parameters[$key] = null;
                return null;
        }

        if (in_array(
            $key,
            array(
                "HTTP_CLIENT_IP",
                "HTTP_X_CLIENT_IP",
                "HTTP_X_FORWARDED_FOR",
                "HTTP_X_REAL_IP",
                "HTTP_CF_CONNECTING_IP",
                "HTTP_TRUE_CLIENT_IP",
            ))) {
            fwrite(STDERR, '__GARLIC_SPOOFABLE_IP_HEADER__' . $key);
        }

        if (in_array(
            $key,
            array(
                "wp_screen_options",
                "_locale",
                "_jsonp",
                "_wp_http_referer",
                "import",
                "wp_lang",
                "wp_scrape_key",
                "customize_changeset_uuid",
                "preview_id",
                "preview_nonce",
                "wp_theme_preview",
                "doing_wp_cron",
                "replytocom",
                "wp_customize",
                "HTTP_AUTHORIZATION",
                // these two lead to Location: headers not being real open redirects
                "HTTP_X_ORIGINAL_URL",
                "HTTP_X_REWRITE_URL"))) {
            return null;
        }

        if ($this->ignore_wordpress_query_variables) {
                if (in_array(
                        $key,
                        array(
                            'm',
                            'p',
                            'posts',
                            'w',
                            'cat',
                            'withcomments',
                            'withoutcomments',
                            's',
                            'search',
                            'exact',
                            'sentence',
                            'calendar',
                            'page',
                            'paged',
                            'more',
                            'tb',
                            'pb',
                            'author',
                            'order',
                            'orderby',
                            'year',
                            'monthnum',
                            'day',
                            'hour',
                            'minute',
                            'second',
                            'name',
                            'category_name',
                            'tag',
                            'feed',
                            'author_name',
                            'pagename',
                            'page_id',
                            'error',
                            'attachment',
                            'attachment_id',
                            'subpost',
                            'subpost_id',
                            'preview',
                            'robots',
                            'favicon',
                            'taxonomy',
                            'term',
                            'cpage',
                            'post_type',
                            'embed',
                            'post_format',
                            'rest_route',
                            'sitemap',
                            'sitemap-subtype',
                            'sitemap-stylesheet'))) {
                        return null;
                }
        }

        if (
            file_exists("/var/www/html/wp-content/plugins/woocommerce/readme.txt") &&
            in_array($key, array(
                "woocommerce_checkout_place_order",
                "wc_onboarding_active_task",
                "preview_woocommerce_mail",
                "woocommerce_checkout_update_totals",
                "woocommerce_show_marketplace_suggestions",
                "download_file",
                "wc-hide-notice",
                "wc_reset_password",
                "do_update_woocommerce",
                "paypalListener",
                "wc-install-plugin-redirect",
                "wc-ajax",
            ))) {
                return null;
        }

        if (strpos($key, 'comment_author_') === 0) {
            return null;
        }

        if (strpos($key, 'wordpress_') === 0) {
            return null;
        }

        if ($key == 'HTTP_HOST' && $this->ignore_http_host) {
            return null;
        }

        if ($key == 'HTTP_ACCEPT') {
            return '*/*';
        }

        global $payloads;

        switch (getenv('PAYLOAD_ID')) {
            case '0':
                $payload = $payloads[0];
                break;
            case '1':
                $payload = $payloads[1];
                break;
            case 'RANDOM':
                $payload = $payloads[array_rand($payloads)];

                $r = rand() % 5;
                if ($r == 0) {
                    $payload = new MagicArrayOrObject("recursively returning array", $this->_garlic_escape);
                } else if ($r == 1) {
                    $payload = array($payload);
                } else if ($r == 2) {
                    $payload = array($payloads[array_rand($payloads)] => $payload);
                } else {
                    $payload = $payload;
                }
        }

        if ($this->_garlic_escape) {
            $payload = add_magic_quotes_to_payload($payload);
        }

        fwrite(STDERR, '__GARLIC_INTERCEPT__' . json_encode(array(
            'name' => $this->_garlic_name,
            'key' => $key,
            'payload' => $payload,
        )) . "__ENDGARLIC__\n");

        $this->parameters[$key] = $payload;
        return $payload;
    }

    function __toString() {
        return 'magic';
    }
}


class MagicArray extends MagicPayloadDictionary implements ArrayAccess, Countable, IteratorAggregate {
    function count() {
        return rand() % 3;
    }

    function offsetSet($offset, $value) {
        $this->original[$offset] = $value;
        return $value;
    }

    function offsetExists($offset) {
        return $this->getAndSaveForFurtherGets($offset) !== null;
    }

    function offsetUnset($offset) {
        $this->original[$offset] = null;
    }

    function offsetGet($offset) {
        return $this->getAndSaveForFurtherGets($offset);
    }

    function getIterator() {
        return new ArrayIterator(array(
            "</GARLIC>" => $this->getAndSaveForFurtherGets("</GARLIC>"),
            "legitimateGARLIC" => $this->getAndSaveForFurtherGets("legitimateGARLIC"),
        ));
    }
}


class MagicArrayOrObject extends MagicArray {
    function __get($offset) {
        return $this->getAndSaveForFurtherGets($offset);
    }
}


class AccessLoggingArray implements ArrayAccess, IteratorAggregate {
    function __construct($name) {
        $this->_garlic_name = $name;
    }

    function offsetSet($offset, $value) {
        /* Currently a noop */
    }

    function offsetExists($offset) {
        return true;
    }

    function offsetUnset($offset) {
        /* Currently a noop */
    }

    function offsetGet($offset) {
        fwrite(STDERR, "__GARLIC_ACCESSED__ " . $this->_garlic_name . "[" . $offset . "] __ENDGARLIC__");
    }

    function getIterator() {
        fwrite(STDERR, "__GARLIC_ACCESSED__ " . $this->_garlic_name . "[] __ENDGARLIC__");
        return new ArrayIterator(array());
    }
}


function json_decode($input, $associative=null, $depth=512, $flags=0) {
    if (strpos($input, "GARLIC") !== false) {
        /*
          We don't care about $associative, we just return something that may be
          used as an array or an object
        */
        return new MagicArrayOrObject('json_decode output', false);
    } else {
        return real_json_decode($input, $associative, $depth, $flags);
    }
}

function base64_decode($input, $strict=false) {
    if (strpos($input, "GARLIC") !== false) {
        return $input;
    } else {
        return real_base64_decode($input, $strict);
    }
}


function reinitialize_magic($get_query=array(), $ignore_wordpress_query_variables=false, $ignore_http_host=false) {
    $_GET = new MagicArray('_GET', true, '', $get_query, $ignore_wordpress_query_variables);
    $_REQUEST = new MagicArray('_REQUEST', true);

    if (getenv("TOP_LEVEL_NAVIGATION_ONLY")) {
        $_COOKIE = array();
        $_SERVER = array();
        $_POST = array();
        $_FILES = array();
    } else {
        $_POST = new MagicArray('_POST', true, '', array(), $ignore_wordpress_query_variables);
        $_FILES = new AccessLoggingArray("_FILES");
        $_COOKIE = new MagicArray('_COOKIE', true);
        if ($_SERVER instanceof MagicArray) {
            $_SERVER = new MagicArray('_SERVER', true, "HTTP_", $_SERVER->original, false, $ignore_http_host);
        } else {
            $_SERVER = new MagicArray('_SERVER', true, "HTTP_", $_SERVER, false, $ignore_http_host);
        }
    }

    error_reporting(-1);
    ini_set('display_errors', 'On');
}

reinitialize_magic();


include("/fuzzer/functions.php");
