This is to skip woocommerce, elementor etc. actions or REST routes if we are
fuzzing any *other* plugin than this one.

For instance, when fuzzing something that has woocommerce as a dependency,
we want to fuzz only the chosen plugin, and fuzz woocommerce routes only when
we picked woocommerce to fuzz.
