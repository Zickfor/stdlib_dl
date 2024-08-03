# StudentLibrary downloader

My small script for saving books from studentlibrary.ru in PDF.

# How to use?
1. Install requerments:
```
pip install pdfkit toml requests re beautifulsoup4
```
**NB!** pdfkit uses wkhtmltopdf you have to install, please, read instructions according to your operating system.
2. Start script.
3. Edit auto created **config.toml**
* In section *auth* edit your SSr. You can get it from studentlibrary.ru url.
* In *ISBNs* put ISBN codes of books.
* Example:
```toml
ISBNs = [ "9785970437834", "9785970470640",]

[auth]
SSr = "07E808021D76A"
```
4. Start script again.
5. Watch the results in books folder!
6. On the next script executions change SSr (if necessary) and ISBNs list.
