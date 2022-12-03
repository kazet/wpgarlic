<?php

/*
 * We do this early, before wp-load, in case some early
 * setup code checks admin permissions
 */
$current_user = new FakeUser(1);
