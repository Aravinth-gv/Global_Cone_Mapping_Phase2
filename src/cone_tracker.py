import numpy as np

class ConeState:
    def __init__(self,cone_id,cone_type,x,y,confidence,config):
        self.cone_id=cone_id
        self.cone_type=cone_type
        self.x=float(x)
        self.y=float(y)
        self.variance=config["initial_position_variance"]
        self.observations=1
        self.confidence_sum=float(confidence)
        self.confidence=float(confidence)
        self.existence_probability=min(1.0,0.35+0.20*confidence)
        self.missed_updates=0
        self.total_updates=1
        self.last_seen=0.0
        self.predicted_updates=0
        self.confirmed=False
        self.config=config

    def update(self,x,y,confidence,timestamp):
        measurement_noise=self.config["measurement_noise"]
        process_noise=self.config["process_noise"]
        measurement_variance=max(
            measurement_noise,
            measurement_noise/max(confidence,0.1)
        )

        kalman_gain=self.variance/(self.variance+measurement_variance)
        self.x+=kalman_gain*(x-self.x)
        self.y+=kalman_gain*(y-self.y)
        self.variance=(1.0-kalman_gain)*self.variance+process_noise

        self.observations+=1
        self.total_updates+=1
        self.confidence_sum+=confidence
        self.confidence=self.confidence_sum/self.observations
        self.existence_probability=min(
            1.0,
            self.existence_probability+0.12*confidence
        )
        self.missed_updates=0
        self.predicted_updates=0
        self.last_seen=timestamp

        if (
            self.observations>=self.config["min_confirmed_observations"]
            and self.existence_probability>=self.config["promotion_threshold"]
        ):
            self.confirmed=True

    def predict(self):
        process_noise=self.config["process_noise"]
        initial_variance=self.config["initial_position_variance"]

        if not self.confirmed:
            self.variance+=process_noise
        else:
            self.variance=min(
                self.variance+process_noise,
                initial_variance
            )

        self.existence_probability*=self.config["ghost_decay"]
        self.missed_updates+=1
        self.total_updates+=1
        self.predicted_updates+=1

    def status(self):
        if self.confirmed:
            return "CONFIRMED"
        if self.existence_probability<=self.config["demotion_threshold"]:
            return "DEMOTED"
        return "TENTATIVE"


class StreamingConeMap:
    def __init__(self,config):
        self.config=config
        self.states=[]
        self.next_cone_id=1
        self.association_count=0
        self.new_state_count=0
        self.promotions=0
        self.demotions=0
        self.peak_active_states=0

    def distance(self,a,b):
        return np.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

    def find_match(self,x,y,cone_type):
        candidates=[]

        for state in self.states:
            if state.cone_type!=cone_type:
                continue

            gate=(
                self.config["reassociation_gate_m"]
                if state.missed_updates>0
                else self.config["association_gate_m"]
            )

            d=self.distance((x,y),(state.x,state.y))

            if d<=gate:
                candidates.append((d,state))

        if not candidates:
            return None

        candidates.sort(key=lambda item:item[0])
        return candidates[0][1]

    def process(self,x,y,confidence,cone_type,timestamp):
        if self.config["prediction_enabled"]:
            for state in self.states:
                state.predict()

        matched_state=self.find_match(x,y,cone_type)

        if matched_state is not None:
            previous_status=matched_state.status()

            matched_state.update(
                x,y,confidence,timestamp
            )

            current_status=matched_state.status()

            if (
                previous_status!="CONFIRMED"
                and current_status=="CONFIRMED"
            ):
                self.promotions+=1

            self.association_count+=1

        elif len(self.states)<self.config["max_active_cones"]:
            new_state=ConeState(
                self.next_cone_id,
                cone_type,
                x,
                y,
                confidence,
                self.config
            )

            new_state.last_seen=timestamp
            self.states.append(new_state)

            self.next_cone_id+=1
            self.new_state_count+=1

        active_states=[]

        for state in self.states:
            status=state.status()

            if (
                status=="DEMOTED"
                and state.missed_updates>self.config["max_missed_updates"]
            ):
                self.demotions+=1
                continue

            active_states.append(state)

        self.states=active_states
        self.peak_active_states=max(
            self.peak_active_states,
            len(self.states)
        )

    def get_states(self):
        return self.states