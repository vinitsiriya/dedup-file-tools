from setuptools import setup, find_packages

setup(
    name="dedup-file-tools",
    version="0.1.2",
    description="Non-Redundant Media File Copy Tool: resumable, auditable, cross-platform, CLI-based.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vinit",
    author_email="vinitsiriya@gmail.com",
    url="https://github.com/vinitsiriya/dedup-file-tools",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pytest",
        "flake8",
        "black",
        "mypy",
        "wmi",
        "tqdm",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "dedup-file-copy-fs=dedup_file_tools_fs_copy.main:main",
            "dedup-file-move-dupes=dedup_file_tools_dupes_move.main:main",
            "dedup-file-compare=dedup_file_tools_compare.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
