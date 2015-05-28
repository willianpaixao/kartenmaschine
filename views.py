from datetime import datetime
from fabric.api import local
import logging
import subprocess
from tempfile import NamedTemporaryFile

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from kartenmaschine.forms import *
from karte.models import *

logger = logging.getLogger(__name__)

class ExportFormView(FormView):
    template_name = "export.html"
    form_class = ExportForm

    def form_valid(self, form):
        return super(ExportFormView, self).form_valid(form)

class ExportView:

    header_template = """
\\documentclass[%(CARDFORMAT)s,%(FONTSIZE)s,%(OPTIONS)sgrid=%(GRID)s]{kartei}

\\usepackage[%(LANGUAGE)s]{babel}

\\begin{document}
"""

    footer= """
\\end{document}
"""

    card_template = """
\\begin{karte}[%(SECTION)s]{
%(FRONT)s}
%(BACK)s
\\end{karte}
"""

    def get_karte(self, id):
        card = Card.objects.get(pk=id)
        card_attr = {
            'SECTION': card.subsection,
            'FRONT': card.front,
            'BACK': card.back
        }
        return (self.card_template % card_attr).encode("utf8")

    def card_export(self, id, header_attr={}):

        default_header_attr = {
            'CARDFORMAT': 'a8paper',
            'FONTSIZE': '12pt',
            'GRID': 'none',
            'OPTIONS': 'flip,',
            'LANGUAGE': 'portuguese'
        }

        if not header_attr:
            header_attr = default_header_attr

        with NamedTemporaryFile(suffix=".tex", delete=False) as f:
            f.write(self.header_template % header_attr)
            f.write(self.get_karte(self.kwargs['pk']))
            f.write(self.footer)
            f.flush()
            self.compile_export(f.name)

    def compile_export(self, file):
        """
        Calls makefile with the given TeX file and compile into PDF.
        I'm currently using Fabric library to run commands. See Fabric's
        documentation for further information.
        """

        logging.info('File "{}" is about to be compiled.'.format(file))
        local("make " + file)

class BoxExportView(TemplateView):

    template_name = "box_export.html"

    header_template = """
\\documentclass[%(CARDFORMAT)s,%(FONTSIZE)s,%(OPTIONS)sgrid=%(GRID)s]{kartei}

\\usepackage[%(LANGUAGE)s]{babel}

\\begin{document}
"""

    footer= """

\\end{document}
"""
    card_template = """
\\begin{karte}[%(SUBSECTION)s]{
%(FRONT)s}
%(BACK)s
\\end{karte}
"""

    def get_context_data(self, **kwargs):
        context = super(BoxExportView, self).get_context_data(**kwargs)
        context['box'] = Box.objects.get(pk=self.kwargs['pk'])
        self.box_export(id=self.kwargs['pk'])
        return context

    def get_karte(self, id):
        card = Card.objects.get(pk=id)
        card_attr = {
            'SUBSECTION': card.subsection,
            'FRONT': card.front,
            'BACK': card.back
        }
        return self.card_template % card_attr

    def get_box_cards(self, id):
        kartes = ""
        secs= Section.objects.filter(box=id)
        for sec in secs:
            subs = Subsection.objects.filter(section=sec.id)
            for sub in subs:
                cards = Card.objects.filter(subsection=sub.id)
                for card in cards:
                    kartes += self.get_karte(id=card.id)
        return kartes

    def box_export(self, id, header_attr={}, file_attr={}):

        default_header_attr = {
            'CARDFORMAT': 'a8paper',
            'FONTSIZE': '12pt',
            'GRID': 'none',
            'OPTIONS': 'print,flip,',
            'LANGUAGE': 'portuguese'
        }

        default_file_attr = {
            'filename': 'box' + id + datetime.now().__format__("%y%m%d%H%M") + '.tex',
            'mode': 'w',
            'path': ''
        }

        if not header_attr:
            header_attr = default_header_attr
        if not file_attr:
            file_attr = default_file_attr

        file = open(file_attr['filename'], file_attr['mode'])
        file.write(self.header_template % header_attr)
        file.write(self.get_box_cards(self.kwargs['pk']))
        file.write(self.footer)
        file.close()
        self.compile_export(file_attr)

    def compile_export(self, file_attr={}):

        subprocess.call(["make", file_attr['filename']])

class SectionExportView(TemplateView):

    template_name = "section_export.html"

    header_template = """
\\documentclass[%(CARDFORMAT)s,%(FONTSIZE)s,%(OPTIONS)sgrid=%(GRID)s]{kartei}

\\usepackage[%(LANGUAGE)s]{babel}

\\begin{document}
"""

    footer= """

\\end{document}
"""
    card_template = """
\\begin{karte}[%(SECTION)s]{
%(FRONT)s}
%(BACK)s
\\end{karte}
"""

    def get_context_data(self, **kwargs):
        context = super(SectionExportView, self).get_context_data(**kwargs)
        context['sec'] = Section.objects.get(pk=self.kwargs['pk'])
        self.section_export(id=self.kwargs['pk'])
        return context

    def get_karte(self, id):
        card = Card.objects.get(pk=id)
        card_attr = {
            'SECTION': card.subsection.section.short,
            'FRONT': card.front,
            'BACK': card.back
        }
        return self.card_template % card_attr

    def get_section_cards(self, id):
        kartes = ""
        subs = Subsection.objects.filter(section=id)
        for sub in subs:
            cards = Card.objects.filter(subsection=sub.id)
            for card in cards:
                kartes += self.get_karte(id=card.id)
        return kartes

    def section_export(self, id, header_attr={}, file_attr={}):

        default_header_attr = {
            'CARDFORMAT': 'a8paper',
            'FONTSIZE': '12pt',
            'GRID': 'none',
            'OPTIONS': 'print,flip,',
            'LANGUAGE': 'portuguese'
        }

        default_file_attr = {
            'filename': 'sec' + id + datetime.now().__format__("%y%m%d%H%M") + '.tex',
            'mode': 'w',
            'path': ''
        }

        if not header_attr:
            header_attr = default_header_attr
        if not file_attr:
            file_attr = default_file_attr

        file = open(file_attr['filename'], file_attr['mode'])
        file.write(self.header_template % header_attr)
        file.write(self.get_section_cards(self.kwargs['pk']))
        file.write(self.footer)
        file.close()
        self.compile_export(file_attr)

    def compile_export(self, file_attr={}):

        subprocess.call(["make", file_attr['filename']])

class SubsectionExportView(TemplateView):

    template_name = "subsection_export.html"

    header_template = """
\\documentclass[%(CARDFORMAT)s,%(FONTSIZE)s,%(OPTIONS)sgrid=%(GRID)s]{kartei}

\\usepackage[%(LANGUAGE)s]{babel}

\\begin{document}
"""

    footer= """

\\end{document}
"""
    card_template = """
\\begin{karte}[%(SECTION)s]{
%(FRONT)s}
%(BACK)s
\\end{karte}
"""

    def get_context_data(self, **kwargs):
        context = super(SubsectionExportView, self).get_context_data(**kwargs)
        context['sub'] = Subsection.objects.get(pk=self.kwargs['pk'])
        self.subsection_export(id=self.kwargs['pk'])
        return context

    def get_karte(self, id):
        card = Card.objects.get(pk=id)
        card_attr = {
            'SECTION': card.subsection.section.short,
            'FRONT': card.front,
            'BACK': card.back
        }
        return self.card_template % card_attr

    def get_subsection_cards(self, id):
        kartes = ""
        cards = Card.objects.filter(subsection=id)
        for card in cards:
            kartes += self.get_karte(id=card.id)
        return kartes

    def subsection_export(self, id, header_attr={}, file_attr={}):

        default_header_attr = {
            'CARDFORMAT': 'a8paper',
            'FONTSIZE': '12pt',
            'GRID': 'none',
            'OPTIONS': 'print,flip,',
            'LANGUAGE': 'portuguese'
        }

        default_file_attr = {
            'filename': 'sub' + id + datetime.now().__format__("%y%m%d%H%M") + '.tex',
            'mode': 'w',
            'path': ''
        }

        if not header_attr:
            header_attr = default_header_attr
        if not file_attr:
            file_attr = default_file_attr

        file = open(file_attr['filename'], file_attr['mode'])
        file.write(self.header_template % header_attr)
        file.write(self.get_subsection_cards(self.kwargs['pk']))
        file.write(self.footer)
        file.close()
        self.compile_export(file_attr)

    def compile_export(self, file_attr={}):

        subprocess.call(["make", file_attr['filename']])

class CardExportView(ExportView, TemplateView):

    template_name = "card_export.html"

    def get_context_data(self, **kwargs):
        context = super(CardExportView, self).get_context_data(**kwargs)
        context['card'] = Card.objects.get(pk=self.kwargs['pk'])
#        self.card_export(id=self.kwargs['pk'])
        return context

