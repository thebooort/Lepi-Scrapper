# Lepi-Scrapper
Lepi Scrapper is a small package to get testual descriptions of lepidoptera species based on internet sources. At the moment it scrapes the following sources:
- [wikipedia](https://www.wikipedia.org/)
- [artfakta](https://artfakta.se/)
- [ukmoths](https://www.ukmoths.org.uk/)
- [nrm](https://www.nrm.se/)
- [animaldiversityweb](https://animaldiversity.org/)
- [butterfliesandmoths.org](https://www.butterfliesandmoths.org/)

Please note that the package is still in development and some features may not work as expected. If you encounter any issues, please open an issue on the GitHub repository.



## Installation
- You need to install libraries `beautifulsoup4`, `requests`, `pandas` and `lxml` to run the code. You can install them using pip:
```bash
pip install beautifulsoup4 requests pandas lxml
``` 
- For some resources you need to have a API key. IN order to work with the code create a file called secrets.json in the root directory of the project. The file should look like this:
```json
{
    "artfakta_api_key": "YOUR API KYE HERE",
  }
```
- You can get the API key from the [artfakta](https://artfakta.se/) website. You need to create an account and then you can get the API key from your profile page.

# Disclaimer

Please note that the data obtained from the sources is subject to their respective terms of use. The package does not store any data and only scrapes the data from the sources when requested.

 Please make sure to comply with the terms of use of the sources when using the package. 
 
 This package is created  for research purposes only and is not intended for commercial use. 
 
 The package is not affiliated with any of the sources and is not responsible for any issues that may arise from the use of the data obtained from the sources.