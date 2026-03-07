from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

import serial
import threading
import time
from datetime import datetime
import numpy as np
import configparser
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import matplotlib
matplotlib.use("Agg")
matplotlib.set_loglevel("WARNING")
import matplotlib.pyplot as plt
import random
#from gpiozero import Button, OutputDevice
from signal import pause
