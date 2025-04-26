
Installation
============

This document provides instructions for installing Augment Adam.

Requirements
------------

* Python 3.8 or higher
* pip
* virtualenv (recommended)

Installation Steps
------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/augment-adam.git
      cd augment-adam

2. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the package:

   .. code-block:: bash

      pip install -e .

4. Verify the installation:

   .. code-block:: bash

      python -c "import augment_adam; print(augment_adam.__version__)"
