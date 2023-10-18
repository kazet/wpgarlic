TIMEOUT_SECONDS = 3

# That means: 50 iterations where each variable (GET, POST param etc.) is replaced with
# a payload, 50 iterations when intercept happens with 50% probability etc.
VARIABLE_INTERCEPT_PROBABILITIES = [100] * 50 + [50] * 50 + [33] * 50 + [25] * 50
