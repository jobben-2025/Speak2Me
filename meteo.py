import requests

def geo(place:str='berlin',country:str='de'):
    n,lang = 1,'en'
    res = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={place}&count={n}&language={lang}')
    res = dict(res.json()).get('results')
    if res != None:
        res = res[0]
        return res

def classify_rain(total) -> str:
    if total == 0 : return "no rain"
    if total < 1  : return "barely any rain"
    if total < 5  : return "mild rain"
    if total < 15 : return "moderate rain"
    if total < 30 : return "heavy rain"
    if total < 50 : return "very heavy rain"
    return "basically a flood ... BUILD AN ARK!"

def classify_cloud(average) -> str:
    if average < 20 : return "a clear sky"
    if average < 60  : return "partly cloudy"
    if average < 85 : return "mostly cloudy"
    return "overcast today"
 
def meteo(geo):
    
    lat,lon = geo['latitude'], geo['longitude']
    latlon = f'latitude={lat}&longitude={lon}'
    #url = f'https://api.open-meteo.com/v1/forecast?{latlon}&hourly=temperature_2m&models=icon_seamless'
    url =  f'https://api.open-meteo.com/v1/forecast?{latlon}&hourly=temperature_2m,rain,relative_humidity_2m,wind_speed_10m,visibility,cloud_cover&forecast_days=1'
    
    met = requests.get(url)
    met = dict(met.json())
    
    
    # TEMP
    temp_u = met['hourly_units']['temperature_2m']
    temps = met['hourly']['temperature_2m']
    temp_low, temp_high, temp_avrg = min(temps), max(temps), sum(temps) / len(temps)

    # RAIN
    rain_u = met['hourly_units']['rain'] #millimeter
    rain = met['hourly']['rain']
    rain_total = sum(rain)
    rain_status = classify_rain(rain_total)
    
    # HUMI
    humi_u = met['hourly_units']['relative_humidity_2m']
    humi = met['hourly']['relative_humidity_2m']
    humi_low, humi_high, humi_avrg = min(humi), max(humi), sum(humi) / len(humi)
  
    # WIND
    wind_u = met['hourly_units']['wind_speed_10m']
    wind = met['hourly']['wind_speed_10m']
    wind_low,wind_high,wind_av = min(wind),max(wind),sum(wind) / len(wind)
    
    # VIS
    vis_u = met['hourly_units']['visibility']
    vis = met['hourly']['visibility']
    vis_low,vis_high,vis_av = min(vis),max(vis),sum(vis) / len(vis)
    
    # Cloud
    cld_u = met['hourly_units']['cloud_cover']
    cld = met['hourly']['cloud_cover']
    cld_low,cld_high,cld_av = min(cld),max(cld),sum(cld) / len(cld)
    cloud_status = classify_cloud(cld_av)
    
    rain_details = f'with a precipitation total of {rain_total:.1f} {rain_u},\n' if rain_total > 0.0 else ''
    
    weather = f"""
Here is the Weather for {geo['name']} / {geo['admin1']} in {geo['country']}:

It is {cloud_status}.
Temperatures range from {temp_low} to {temp_high} {temp_u}, 
with an average of {temp_avrg:.1f} {temp_u}, with

windspeeds reaching up to: {wind_high} {wind_u}

Furthermore, there is {rain_status} today,
{rain_details} and an average humidity of {humi_avrg:.1f} {humi_u}.


In case you were planning a roadtrip, here is the average visibility for today: {int(vis_av)} {vis_u}

SkyNET has noted this location has a population of {geo['population']} human beeings.

This might be taken into account on the next scheduled purge cleaning program.
"""
    #return {'report': weather, 'geo':geo, 'met':met}
    return weather


    
def weather(place:str,country:str='de'):
    try:
        return meteo(geo(place,country))
    except:
        return 'failed to get weather'
    
