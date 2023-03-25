# EDA Tool

[![License: Apache License 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Forks](https://img.shields.io/github/forks/hipnologo/eda-tool)](https://github.com/hipnologo/eda-tool/network/members)
[![Stars](https://img.shields.io/github/stars/hipnologo/eda-tool)](https://github.com/hipnologo/eda-tool/stargazers)
[![Issues](https://img.shields.io/github/issues/hipnologo/eda-tool)](https://github.com/hipnologo/eda-tool/issues)

This is a Flask app integrated with Dash, which allows users to upload a CSV or Excel file, and then filter and display the data on a Dashboard page. The app includes the following features:

* Upload a file and save it in a session-specific directory.
* Read the uploaded file and process the data.
* Generate a dashboard with a data table and KPI (Key Performance Indicator) container.
* Filter the data by categorical and date columns.
* Display the filtered data in the data table and KPI container.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

This app is built using Python and Streamlit, and leverages a variety of Python libraries and machine learning models to achieve automated machine learning results.

* [Python](https://www.python.org/) - A high-level programming language used for general-purpose programming.
* [Flask](https://flask.palletsprojects.com) - Flask is a micro web framework written in Python.
* [Dash](https://pypi.org/project/dash/) - Dash is the most downloaded, trusted Python framework for building ML & data science web apps.
* [numpy](https://numpy.org/) - A Python library for working with arrays and matrices.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started
### Prerequisites

To install the dependencies required for this app:
* Python Libraries
  ```sh
   pip3 install -r requirements.txt
  ```

### Installation

_Follow the steps below to ensure you can have all the necessary to run this app._

1. Clone the repo
   ```sh
   git clone https://github.com/hipnologo/eda-tool.git
   ```
2. Install Python packages
   ```sh
   pip3 install -r requirements.txt
   ```
3. Run the Streamlit app and redirect its output to the log file.
   ```sh
   nohup streamlit run app.py > app.log 2>&1 &
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing

We welcome contributions to this project! If you have an idea for a feature or bug fix, follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes to the new branch.
4. Push the branch to your forked repository.
5. Submit a pull request to the original repository.

Make sure to follow the code style and add test cases for any new code. If you have any questions, don't hesitate to ask the repository maintainers.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the Apache License 2.0. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Fabio Carvalho - [@fabioac](https://twitter.com/fabioac)

Project Link: [https://github.com/hipnologo/eda-tool](https://github.com/hipnologo/eda-tool)

<p align="right">(<a href="#top">back to top</a>)</p>
