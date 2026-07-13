from setuptools import setup

setup(name='CASCADE',
      entry_points={
          'console_scripts': [
              'CASCADE = cascade.CLI:main',
          ],
      },
      install_requires=[
          'tqdm==4.67.3',
          'openai==2.31.0',
          'docker==7.1.0',
          'tiktoken==0.12.0',
          'matplotlib==3.10.8',
          'httpx==0.28.1'
      ],
      include_package_data=True
)