from setuptools import setup, find_packages

print(find_packages(where='src'))  # Debugging: Print detected packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='oas_patch',
    version='0.3.7',
    description='A tool to apply overlays to OpenAPI documents, and create an overlay from the difference of 2 openapi files.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Matthieu Croissant',
    url='https://github.com/mcroissant/oas_patcher',
    packages=find_packages(where='src'),  # Automatically find all packages in 'src'
    package_dir={'': 'src'},  # Root of the package is 'src'
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    install_requires=[
        'PyYAML>=6.0',
        'jsonpath-ng>=1.7.0',
        'jsonschema>=4.23.0',
        'deepdiff>=8.4.2'
    ],
    entry_points={
        'console_scripts': [
            'oas-patch=oas_patch.oas_patcher_cli:cli',  # Reference the CLI entry point
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
)
