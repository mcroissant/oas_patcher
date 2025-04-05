from setuptools import setup, find_packages

print(find_packages(where='src'))  # Debugging: Print detected packages

setup(
    name='oas_patch',
    version='0.0.4',
    description='A tool to apply overlays to OpenAPI documents.',
    author='Matthieu Croissant',
    url='https://github.com/mcroissant/oas_patcher',
    packages=find_packages(where='src'),  # Automatically find all packages in 'src'
    package_dir={'': 'src'},  # Root of the package is 'src'
    install_requires=[
        'PyYAML>=6.0',
        'jsonpath-ng>=1.7.0'
    ],
    entry_points={
        'console_scripts': [
            'oas-patch=oas_patch.oas_patcher_cli:cli',  # Reference the CLI entry point
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3.7',
)
