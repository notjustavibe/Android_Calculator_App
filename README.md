## Qasim Calculator

A modern calculator app built with Python and the Kivy framework, packaged as a native 
Android APK using Buildozer and python-for-android.

### Features
- Standard arithmetic operations with a scientific mode
- Calculation history
- Unit converters: Length, Area, Volume, Weight, Speed, Pressure, Power, Temperature
- Number system converter (Binary, Octal, Decimal, Hexadecimal)
- Custom-styled UI with rounded cards, icon navigation, and screen transitions

### Built with
- Python 3.11
- Kivy 2.3.1
- Buildozer / python-for-android

### Running locally
pip install kivy
python main.py

### Building the APK
buildozer -v android debug

### Roadmap
- [ ] Currency conversion (live rates)
