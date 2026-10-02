# Generic AI adapter guidance

Use `START_HERE.md` as the PMO runtime entrypoint at the beginning of each new session. Keep provider-specific instructions thin and provider-neutral behavior in PMO itself.

Honor Config, correction precedence, canonical-vs-generated boundaries and the System/Config/Data write boundary. Never claim a read or write succeeded when the provider connection could not perform it.
