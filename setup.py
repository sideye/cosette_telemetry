import setuptools

setuptools.setup(
	name = "cosette_telemetry",
	version = "0.0.1",
	author = "Alan Liang",
	author_email = "alanliang@berkeley.edu",
	description = "Cosette telemetry plug in for Otter",
	packages = setuptools.find_packages(exclude=["test"]),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
	],
	install_requires=[
		"setuptools", "pandas", "gspread"
	]
)
