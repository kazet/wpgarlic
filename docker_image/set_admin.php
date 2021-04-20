<?php

class FakeAdmin {
	function __construct() {
		$this->ID = 1;
	}
}

/*
 * We do this early, before wp-load, in case some early
 * setup code checks admin permissions
 */
$current_user = new FakeAdmin();
