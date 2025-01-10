from dataclasses import dataclass, fields
from typing import Mapping, List 

@dataclass 
class SubscriptionDTO:
    email: str 
    subs_and_cutoffs : List[Mapping[str, int]]

    def to_ddb_item(self) -> Mapping[str, str | int]: 
        result = {}
        for field in fields(self):
            field_name = field.name
            field_value = getattr(self, field_name)
            result[field_name] = field_value 
        return result
    
    @classmethod
    def from_ddb_item(cls, ddb_item: Mapping[str, str | int]) -> 'SubscriptionDTO':
        subs_and_cutoffs = ddb_item['subs_and_cutoffs']
        new_subs_and_cutoffs = []
        for sub_and_cutoff in subs_and_cutoffs:
            converted = {sub: int(cutoff) for sub, cutoff in sub_and_cutoff.items()}
            new_subs_and_cutoffs.append(converted)
        ddb_item['subs_and_cutoffs'] = new_subs_and_cutoffs
        return SubscriptionDTO(**ddb_item)