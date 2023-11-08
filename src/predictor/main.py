import pandas as pd

from src.predictor.ability_predictor import AbilityPredictor

if __name__ == "__main__":
    network = 'Winamax.fr'
    df = pd.read_json('tmp.json')
    ap = AbilityPredictor(network)
    prediction = ap.predict(df)
    print(prediction.columns)
    prediction['buyin'] = prediction['@rake'] + prediction['@stake']
    for buyin in sorted(prediction['buyin'].unique().tolist()):
        print(prediction[prediction['buyin'] == buyin])
    print(prediction)
