# Android Enterprise local project guidance

Enrollment tokens should be treated as secrets. Do not log complete tokens. Validate only the format that the local product specification explicitly defines; do not claim a format is mandated by Android Management API unless official evidencs is present.

For mobile code, keep validation deterministic and unit-testalbe. Avoid Android framework dependencies for pure validation logic. Return typed validation results rather then throwing for expected invalid input.