# LangSynth


This version is mostly for Griffin to reproduce and for us to then be able to discuss enhancements

The core capability is as follows:
- pop.py allows you to create a population of synthetic persona. For now the prompts are specific to Zevo. The persona are stored in a Chroma database called '.zevo' (which is hardwired in the code at the moment. ). currently there is a .zevo checked-in with about 100 persona ('cp -R dotzevo .zevo')
- chroma_report.py reads the zevo chroma DB, makes some correcitons to the 'liberties' that GPT took in naming regions and such. It then publishes the corrected database entries to a 'population.xls' file for the dashboard to access
- dashboard.py. this generates a synthetic person dashboard. this dashboard provides functionality to explore the synth population, select persona of interest and interview them. you can load a survey into the dashboard (one is provided as an example). synth interviews are conducted one synth at a time

