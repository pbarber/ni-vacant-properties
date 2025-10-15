# NI vacant properties analysis

Python scripts to take LPS-published tables from [Open Data NI](https://admin.opendatani.gov.uk/dataset/quarterly-property-vacancy-rates-by-district-council-and-sector) and convert to CSV for use in data visualisations.

## Libraries used

* [requests](https://requests.readthedocs.io/en/latest/) to load the page containing the data via HTTP
* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) to parse the HTML
* [pandas](https://pandas.pydata.org/) to process the data

## Example data visualisation

Flourish [interactive version](https://flo.uri.sh/visualisation/24814498/embed?auto=1).

<div class="flourish-embed flourish-chart" data-src="visualisation/24814498"><noscript><img src="https://public.flourish.studio/visualisation/24814498/thumbnail" width="100%" alt="chart visualization" /></noscript></div>
