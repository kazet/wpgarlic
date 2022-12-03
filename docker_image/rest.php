<?php

class Fake_WP_REST_Request extends WP_REST_Request {

    public function __construct($route) {
        global $payloads;
        $methods = array("GET", "HEAD", "POST", "PUT", "DELETE");
        $this->method = $methods[array_rand($methods)];
        $this->headers = new MagicArray('rest_headers', false);
        $this->params = new MagicArray('rest_params', false);
        $this->url_params = new MagicArray('rest_url_params', false);
        $this->query_params = new MagicArray('rest_query_params', false);
        $this->body_params = new MagicArray('rest_body_params', false);
        $this->file_params = new MagicArray('rest_file_params', false);
        $this->default_params = new MagicArray('rest_default_params', false);
        $this->body = add_magic_quotes_to_payload($payloads[array_rand($payloads)]);
        $this->json_params = new MagicArray('rest_json_params', false);
        $this->route = $route;
    }

    public function set_method($method) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_method")) .
            "__ENDGARLIC__");
    }

    public function set_header($key, $value) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_header")) .
            "__ENDGARLIC__");
    }

    public function add_header($key, $value) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "add_header")) .
            "__ENDGARLIC__");
    }

    public function remove_header($key) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "remove_header")) .
            "__ENDGARLIC__");
    }

    public function set_headers($headers, $override = true) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_headers")) .
            "__ENDGARLIC__");
    }

    public function get_header($key) {
        return $this->headers[$key];
    }

    public function get_header_as_array($key) {
        return $this->headers[$key];
    }

    public function get_headers() {
        return $this->headers;
    }

    public function is_json_content_type() {
        return rand() % 2;
    }

    public function get_param($key) {
        return $this->params[$key];
    }

    public function has_param($key) {
        return $this->params[$key] !== NULL;
    }

    public function set_param($key, $value) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_param")) .
            "__ENDGARLIC__");
    }

    public function get_params() {
        return $this->params;
    }

    public function get_url_params() {
        return $this->url_params;
    }

    public function set_url_params($params) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_url_params")) .
            "__ENDGARLIC__");
    }

    public function get_query_params() {
        return $this->query_params;
    }

    public function set_query_params($params) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_query_params")) .
            "__ENDGARLIC__");
    }

    public function get_body_params() {
        return $this->body_params;
    }

    public function set_body_params($params) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_body_params")) .
            "__ENDGARLIC__");
    }

    public function get_file_params() {
        return $this->file_params;
    }

    public function set_file_params($params) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_file_params")) .
            "__ENDGARLIC__");
    }

    public function get_default_params() {
        return $this->default_params;
    }

    public function set_default_params($params) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_default_params")) .
            "__ENDGARLIC__");
    }

    public function get_body() {
        return $this->body;
    }

    public function set_body($data) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_body")) .
            "__ENDGARLIC__");
    }

    public function get_json_params() {
        return $this->json_params;
    }

    public function get_route() {
        return $this->route;
    }

    public function set_route($route) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_route")) .
            "__ENDGARLIC__");
    }

    public function get_attributes() {
        return NULL;
    }

    public function set_attributes($attributes) {
        fwrite(
            STDERR,
            "__GARLIC_NOT_IMPLEMENTED__" .
            json_encode(array("type" => "not_implemented", "class" => "WP_REST_Request", "method" => "set_attributes")) .
            "__ENDGARLIC__");
    }

    public function sanitize_params() {
    }

    public function has_valid_params() {
        return true;
    }

    function offsetSet($offset, $value) {
        /* Currently a noop */
    }

    function offsetExists($offset) {
        return $this->params->offsetExists($offset);
    }

    function offsetUnset($offset) {
        /* Currently a noop */
    }

    function offsetGet($offset) {
        return $this->params->offsetGet($offset);
    }

}

function __garlic_is_allowed($result) {
    if ($result instanceof WP_Error) {
        return false;
    }

    return $result;
}

function do_rest_route_with_user($id, $username) {
    global $_garlic_the_route;

    wp_set_current_user($id, $username);

    foreach (rest_get_server()->get_routes() as $key => $handlers) {
	    if ((string) $key != $_garlic_the_route[0]) {
    		continue;
	    }

    	foreach($handlers as $handler_key => $handler) {
	    	if ((string) $handler_key != $_garlic_the_route[1]) {
		    	continue;
    		}

	    	$request = new Fake_WP_REST_Request($key);
		    if (
                    (!array_key_exists('permission_callback', $handler)) ||
                    (__garlic_is_allowed(call_user_func($handler['permission_callback'], $request)))) {
    			call_user_func($handler['callback'], $request);
	    	}
        }
    }
}
