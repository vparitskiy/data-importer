#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.db import models
from data_importer.importers.xml_importer import XMLImporter


class Musics(models.Model):
    name = models.CharField(max_length=100)
    encoder = models.CharField(max_length=100)
    bitrate = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        return self.full_clean() == None


sxml="""
<encspot>
  <file>
   <Name>some filename.mp3</Name>
   <Encoder>Gogo (after 3.0)</Encoder>
   <Bitrate>131</Bitrate>
  </file>
  <file>
   <Name>another filename.mp3</Name>
   <Encoder>iTunes</Encoder>
   <Bitrate>128</Bitrate>
  </file>
</encspot>
"""


class TestXMLImporter(TestCase):

    def setUp(self):
        class TestXML(XMLImporter):
            root = 'file'
            fields = ['name', 'encoder', 'bitrate']

        self.importer = TestXML(source=sxml)

    def test_read_content(self):
        self.assertEquals(self.importer.cleaned_data[0], (0, {'bitrate': '131',
                          'name': 'some filename.mp3', 'encoder': 'Gogo (after 3.0)'}))

    def test_values_is_valid(self):
        self.assertTrue(self.importer.is_valid())


class TestXMLCleanImporter(TestCase):

    def setUp(self):
        class TestXML(XMLImporter):
            root = 'file'
            fields = ['name', 'encoder', 'bitrate']

            def clean_name(self, value):
                return str(value).upper()

        self.importer = TestXML(source=sxml)

    def test_read_content(self):
        self.assertEquals(self.importer.cleaned_data[0], (0, {'bitrate': '131',
                          'name': 'SOME FILENAME.MP3', 'encoder': 'Gogo (after 3.0)'}))

    def test_values_is_valid(self):
        self.assertTrue(self.importer.is_valid())


class TestXMLModelImporter(TestCase):

    def setUp(self):
        class TestXML(XMLImporter):
            root = 'file'

            class Meta:
                model = Musics

            def clean_name(self, value):
                return str(value).upper()

        self.importer = TestXML(source=sxml)

    def test_model_fields(self):
        self.assertEquals(self.importer.fields, ['name', 'encoder', 'bitrate'])

    def test_read_content(self):
        content = {'bitrate': '131',
        'encoder': 'Gogo (after 3.0)',
        'name': 'SOME FILENAME.MP3'}
        self.assertEquals(self.importer.cleaned_data[0], (0, content))

    def test_values_is_valid(self):
        self.assertTrue(self.importer.is_valid())

    def test_save_data(self):
        for row, data in self.importer.cleaned_data:
            instace = Musics(**data)
            self.assertTrue(instace.save())
