TIMEOUT_SECONDS = 3

# That means: 20 iterations where each variable (GET, POST param etc.) is replaced with
# a payload, 30 iterations when intercept happens with 50% probability etc.
VARIABLE_INTERCEPT_PROBABILITIES = [100] * 20 + [50] * 30 + [33] * 30 + [25] * 20
