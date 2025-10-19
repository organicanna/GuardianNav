from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="guardiannav",
    version="0.1.0",
    author="Anna",
    author_email="your.email@example.com",
    description="Agent de sécurité personnelle basé sur IA, surveillant le trajet d'un utilisateur et déclenchant une assistance en cas d'anomalie.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/organicanna/GuardianNav",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "guardiannav=guardian.guardian_agent:main",
        ],
    },
    include_package_data=True,
    package_data={
        "guardian": ["*.py"],
    },
)
