import SpaceBridge.sbgui

links = [{'id':1,
    'devicename':'Device #1',
    'deviceid':5},
    {'id':2,
    'devicename':'Device #2',
    'deviceid':7}]

pfg = SpaceBridge.sbgui.PortForwardGui("SpaceBridge v0.1")
pfresult = pfg.prompt_for_forwards(links)
print(str(pfresult))



