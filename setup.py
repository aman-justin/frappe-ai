from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_ai_form_builder/__init__.py
from frappe_ai_form_builder import __version__ as version

setup(
	name="frappe_ai_form_builder",
	version=version,
	description="AI-powered form and template generator for Frappe",
	author="Your Name",
	author_email="your.email@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
