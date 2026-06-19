from flask import Blueprint, jsonify, request, Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, date
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.multipart import MIMEMultipart 
import smtplib 
import requests
import time
from flask_wtf.csrf import CSRFProtect
import random
import threading
import re

db =  SQLAlchemy()
migrate = Migrate()