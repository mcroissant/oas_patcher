from setuptools import setup, find_packages

setup(
    name='oas_patch',
    version='1.0.0',
    description='A tool to apply overlays to OpenAPI documents.',
    author='Matthieu Croissant',
    author_email='your.email@example.com',
    url='https://github.com/mcroissant/oas_patcher',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyYAML>=6.0',
        'jsonpath-ng>=1.7.0'
    ],
    entry_points={
        'console_scripts': [
            'oas-patch=oas_patcher_cli:cli',  # Update this to reference the correct module
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)