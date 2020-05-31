import io
import yaml

from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_ES

seed = 42

def init_engine_es():
    engine = SnipsNLUEngine(config=CONFIG_ES, random_state=seed)
    with io.open("GPC_541_Terapia_intravenosa_AETSA_compl.pdf_intent.yml") as f:
        dataset = yaml.load(f)

    engine.fit(dataset)

    engine.parse("Please give me some lights in the entrance !")