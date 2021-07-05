![Python Version][python-shield]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h2 align="center">NetTruyen Downloader Script</h2>

  <p align="center">
    Python script of <a href=https://github.com/quantrancse/nettruyen-downloader>Nettruyen Downloader</a>
    <br />
    <br />
  </p>
</p>

<!-- ABOUT -->
## About
[Update: 07-05-2021] This tool is working.

[Other] I've found a Tampermonkey script that works on different manga sites: https://github.com/lelinhtinh/Userscript/tree/master/manga_comic_downloader

Thanks to the author and use it by your own way.

---

For more infomation about the project please read in [Nettruyen Downloader](https://github.com/quantrancse/nettruyen-downloaderm).

<!-- GETTING STARTED -->
## Usage

The script will download into current working directory.

### Prerequisites

* python 3.8.2
* bs4
* argparse
```sh
pip install argparse bs4 requests
```
### Run the script
```sh
usage: nettruyen_downloader_script.py [-h] [-a] [-f from_chapter to_chapter]
                                      [-c chapter]
                                      manga_url

positional arguments:
  manga_url             url to the manga homepage

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             download/update all chapter
  -f from_chapter to_chapter, --fromto from_chapter to_chapter
                        download from one chapter to another chapter
  -c chapter, --chapter chapter
                        download one chapter
```

## Recommended Manga Viewer

* I have found a good image viewer application that perfectly suited for reading manga - [QuickViewer](https://kanryu.github.io/quickviewer/)
  
<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE][license-url] for more information.

<!-- CONTACT -->
## Contact

* **Author** - [@quantrancse](https://www.facebook.com/quantrancse)

<!-- MARKDOWN LINKS & IMAGES -->
[python-shield]: https://img.shields.io/badge/python-3.8.2-blue?style=flat-square
[license-shield]: https://img.shields.io/github/license/quantrancse/nettruyen-downloader?style=flat-square
[license-url]: https://github.com/quantrancse/nettruyen-downloader-script/blob/master/LICENSE
