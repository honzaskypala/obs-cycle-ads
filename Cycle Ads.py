import obspython as S

DEFAULT_INTERVAL = 5*60   # default interval is 5 minutes

class AdCycler:
    def __init__(self):
        self.timer_on = False
        self.interval = DEFAULT_INTERVAL
    
    def start_pressed(self, props, prop):
        if not self.timer_on:
            self.timer_on = True
            self.old_interval = self.interval
            S.timer_add(self.ticker, self.interval * 1000)
    
    def stop_pressed(self, props, prop):
        self.timer_on = False

    def ticker(self):
        if self.timer_on:
            current_scene = S.obs_scene_from_source(S.obs_frontend_get_current_scene())
            ads = tuple(filter(lambda x: x[:3] == "ad_", [S.obs_source_get_name(i) for i in S.obs_enum_sources()]))
            if (len(ads) == 1):  # if only one ad, then just restart playing the video
                S.obs_source_media_restart(S.obs_get_source_by_name(ads[0]))
            elif (len(ads) > 1): # if more than one ad, then hide the current one and show the next one; showing next one will automatically restart the video the play
                ad_to_show = ads[0]
                visible_ad_found = False
                for ad in ads:
                    if visible_ad_found:
                        ad_to_show = ad
                        break
                    scene_item = S.obs_scene_find_source(current_scene, ad)
                    if S.obs_sceneitem_visible(scene_item):
                        S.obs_sceneitem_set_visible(scene_item, False)
                        visible_ad_found = True
                S.obs_sceneitem_set_visible(S.obs_scene_find_source(current_scene, ad_to_show), True)
            S.obs_scene_release(current_scene)
            if self.interval != self.old_interval: # if interval changed, update it
                S.remove_current_callback()
                self.old_interval = self.interval
                S.timer_add(self.ticker, self.interval * 1000)
        else:
            S.remove_current_callback()

ad_cycler = AdCycler()

def script_defaults(settings):
    S.obs_data_set_default_int(settings, "interval", DEFAULT_INTERVAL)

def script_update(settings):
    ad_cycler.interval = S.obs_data_get_int(settings, "interval")

def script_properties():  # ui
    props = S.obs_properties_create()
    S.obs_properties_add_button(props, "startButton", "Start", lambda x,y: AdCycler.start_pressed(ad_cycler, x, y))
    S.obs_properties_add_button(props, "stopButton", "Stop", lambda x,y: AdCycler.stop_pressed(ad_cycler, x, y))
    interval = S.obs_properties_add_int(props, "interval", "Interval (seconds)", 1, 3600, 300)
    return props

def script_description():
    return "Cycles sources starting with \"ad_\" in their name in given interval"