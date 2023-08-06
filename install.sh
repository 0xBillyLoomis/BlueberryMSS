#!/bin/bash

# Function to install python
install_python() {
  echo "Python is not installed, installing Python..."
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install python3 python3-pip -y
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Install Homebrew if not already installed
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python3
  else
    echo "Unsupported OS, please install Python manually."
    exit 1
  fi
  echo "Python installed successfully."
}

# Function to install packages
install_packages() {
  echo "Installing requests and toml..."
  pip3 install requests toml
  echo "Packages installed successfully."
}

# Check if Python 3 or greater is installed
python_version=$(python3 -V 2>&1 | grep -Po '(?<=Python )\d\.\d')
if [[ -z "$python_version" ]]; then
  install_python
else
  major_version=$(echo $python_version | cut -d. -f1)
  if [[ $major_version -ge 3 ]]; then
    echo "Python version is 3 or greater, proceeding to install packages..."
    install_packages
  else
    echo "Python version is less than 3, installing latest Python version..."
    install_python
    install_packages
  fi
fi
