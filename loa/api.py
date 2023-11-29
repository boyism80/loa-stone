import time
import requests

ENGRAVE_MAP = { '각성': 255, '갈증': 286, '강령술': 243, '강화 무기': 129, '강화 방패': 242, '결투의 대가': 288, '고독한 기사': 225, '공격력 감소': 800, '공격속도 감소': 802, '광기': 125, '광전사의 비기': 188, '구슬동자': 134, '굳은 의지': 123, '그믐의 경계': 312, '극의: 체술': 190, '급소 타격': 142, '기습의 대가': 249, '긴급구조': 302, '넘치는 교감': 199, '달의 소리': 287, '달인의 저력': 238, '돌격대장': 254, '두 번째 동료': 258, '마나 효율 증가': 168, '마나의 흐름': 251, '만개': 306, '만월의 집행자': 311, '멈출 수 없는 충동': 281, '바리케이드': 253, '방어력 감소': 801, '버스트': 279, '번개의 분노': 246, '부러진 뼈': 245, '분노의 망치': 196, '분쇄의 주먹': 236, '불굴': 235, '사냥의 시간': 290, '상급 소환사': 198, '선수필승': 244, '세맥타통': 256, '속전속결': 300, '슈퍼 차지': 121, '승부사': 248, '시선 집중': 298, '실드 관통': 237, '심판자': 282, '아드레날린': 299, '아르데타인의 기술': 284, '안정된 상태': 111, '약자 무시': 107, '에테르 포식자': 110, '여신의 가호': 239, '역천지체': 257, '예리한 둔기': 141, '오의 강화': 127, '오의난무': 292, '완벽한 억제': 280, '원한': 118, '위기 모면': 140, '이동속도 감소': 803, '이슬비': 308, '일격필살': 291, '잔재된 기운': 278, '저주받은 인형': 247, '전문의': 301, '전투 태세': 224, '절실한 구원': 195, '절정': 276, '절제': 277, '점화': 293, '정기 흡수': 109, '정밀 단도': 303, '죽음의 습격': 259, '중갑 착용': 240, '중력 수련': 197, '진실된 용맹': 194, '진화의 유산': 285, '질량 증가': 295, '질풍노도': 307, '처단자': 310, '초심': 189, '최대 마나 증가': 167, '추진력': 296, '축복의 오라': 283, '충격 단련': 191, '타격의 대가': 297, '탈출의 명수': 202, '포격 강화': 193, '포식자': 309, '폭발물 전문가': 241, '피스메이커': 289, '핸드거너': 192, '화력 강화': 130, '환류': 294, '황제의 칙령': 201, '황후의 은총': 200, '회귀': 305 }
PENALTY_MAP = { '공격력 감소': 800, '공격속도 감소': 802, '방어력 감소': 801, '이동속도 감소': 803 }
STAT_MAP = { '치명': 15, '특화': 16, '제압': 17, '신속': 18, '인내': 19, '숙련': 20 }
CATEGORY_MAP = { '목걸이': 200010, '귀걸이': 200020, '반지': 200030 }

class auction_builder:
    def __init__(self):
        self.__level = {'min': 0, 'max': 0}
        self.__quality = 0
        self.__skill_options = []
        self.__engraves = []
        self.__stats = []
        self.__sort = 'BUY_PRICE'
        self.__sort_asc = True
        self.__tier = 3
        self.__grade = '유물'
        self.__page= 1
        self.__name = None
        self.__category = '목걸이'

    def level(self, min=None, max=None):
        if not min and not max:
            return self.__level
        
        else:
            if min is not None:
                self.__level['min'] = min
            if max is not None:
                self.__level['max'] = max
            return self
    
    def quality(self, value=None):
        if not value:
            return self.__quality
        else:
            self.__quality = value
            return self
    
    def engrave(self, name, min=None, max=None):
        if not name:
            return self.__engraves
        else:
            self.__engraves.append({'name': name, 'min': min, 'max': max})
            return self
    
    def penalty(self, name, min=None, max=None):
        return self.engrave(name, min, max)
    
    def stat(self, name, min=None, max=None):
        if not name:
            return self.__stats
        else:
            self.__stats.append({'name': name, 'min': min, 'max': max})
            return self
    
    def sort(self, value, asc=True):
        if not value:
            return self.__sort
        else:
            self.__sort = value
            self.__sort_asc = asc
            return self
    
    def tier(self, value=None):
        if not value:
            return self.__tier
        else:
            self.__tier = value
            return self
    
    def grade(self, value=None):
        if not value:
            return self.__grade
        else:
            self.__grade = value
            return self
    
    def page(self, value=None):
        if not value:
            return self.__page
        else:
            self.__page = max(1, value)
            return self
    
    def name(self, value=None):
        if not value:
            return self.__name
        else:
            self.__name = value
            return self

    def category(self, value=None):
        if not value:
            return self.__category
        else:
            self.__category = value
            return self

    def __build_engrave_option(self):
        return [{'FirstOption': 3, 'SecondOption': ENGRAVE_MAP[x['name']], 'MinValue': x['min'], 'MaxValue': x['max']} for x in self.__engraves]
    
    def __build_stat_option(self):
        return [{'FirstOption': 2, 'SecondOption': STAT_MAP[x['name']], 'MinValue': x['min'], 'MaxValue': x['max']} for x in self.__stats]

    def build(self):
        return {
            'ItemLevelMin': self.__level['min'],
            'ItemLevelMax': self.__level['max'],
            'ItemGradeQuality': self.__quality,
            'SkillOptions': [{'FirstOption': None, 'SecondOption': None, 'MinValue': None, 'MaxValue': None}],
            'EtcOptions': [*self.__build_engrave_option(), *self.__build_stat_option()],
            'Sort': self.__sort,
            'CategoryCode': CATEGORY_MAP[self.__category],
            'CharacterClass': None,
            'ItemTier': self.__tier,
            'ItemGrade': self.__grade,
            'ItemName': self.__name,
            'PageNo': self.__page,
            'SortCondition': 'ASC' if self.__sort_asc else 'DESC',
        }
    
    def search(self, token):
        while True:
            response = requests.post("https://developer-lostark.game.onstove.com/auctions/items", json=self.build(), headers={'Authorization': f'Bearer {token}'})
            if response.status_code != 200:
                raise Exception('cannot request to lost ark auction api')
            
            data = response.json()
            if data is not None:
                break
            time.sleep(1)

        if not data['Items']:
            return

        for item in data['Items']:
            engraves = {}
            stats = {}
            penalty = None
            for option in item['Options']:
                if option['Type'] == 'STAT':
                    stats[option['OptionName']] = option['Value']
                elif option['Type'] == 'ABILITY_ENGRAVE':
                    if not option['IsPenalty']:
                        engraves[option['OptionName']] = option['Value']
                    else:
                        penalty = {option['OptionName']: option['Value']}
            
            yield {
                'name': item['Name'],
                'quality': item['GradeQuality'],
                'price': item['AuctionInfo']['BuyPrice'],
                'trade count': item['AuctionInfo']['TradeAllowCount'],
                'stats': stats,
                'engraves': engraves,
                'penalty': penalty
            }