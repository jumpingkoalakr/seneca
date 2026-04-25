# seneca · 투자 모의주행 시뮬레이터

> "We suffer more often in imagination than in reality."  
> — Lucius Annaeus Seneca, *Letters from a Stoic*, 13.4

> "The hidden risks of being wrong outweigh the rewards of being right.  
> Don't cross a river if it is, on average, 4 feet deep."  
> — Nassim Nicholas Taleb, *Antifragile*, 2012

11자산 다변량 GBM 몬테카를로로 **하위 10% 시나리오**를 주 단위로 체험하며, 폭락 구간에서 **존버·물타기·손절** 결정을 미리 연습하는 도구. 손실 면역(Loss Immunity Training)을 위한 단일 HTML 자기충족 앱.

## 사용법

1. **`index.html`을 브라우저로 연다** — 외부 의존성은 Pretendard 폰트 CDN뿐(없어도 시스템 폰트로 폴백).
2. **자산 배분 선택** — S&P500 100% / NASDAQ100 100% / 코스피200 100% / 비트코인 100% / 분산 투자 (주식 50% 기타 50%) 5개 프리셋, 또는 "직접 입력"으로 11자산 비중을 수동 조정 (합계 100% 필수).
3. **투자금·기간 조절** — 100만-5억원, 1-10년 (기본 3년).
4. **`스트레스 테스트 시작`** — 하위 10% 시나리오가 주 단위로 전개. 드로우다운 -5%마다 결정 패널 등장:
   - 현재 경기 국면 (4국면 중) + 가장 많이 하락한 자산 + 그럴듯한 한국 경제 뉴스 헤드라인
   - 존버 / 물타기(+S0 추가) / 손절(전량 매도→원화 현금) 3개 옵션
5. **결과 패널** — 최종가치·수익률, 비교(중앙값/끝까지 보유), 거시 흐름 타임라인, 4국면 학습 카드.

URL 쿼리 `?p=10|50|90` 또는 차트 우상단 ⚙ 메뉴에서 시나리오 분위를 바꿀 수 있다 (기본 하위 10%).

## 시뮬레이션 모델

### 자산군 (11종, KRW 기준 총수익률)

| # | 자산 | μ (연) | σ (연) | 데이터 기간 |
|---|---|---|---|---|
| 0 | S&P500 (KRW환산) | 10.0% | 18% | 1990–2024 |
| 1 | NASDAQ100 (KRW환산) | 13.0% | 24% | 1990–2024 |
| 2 | 코스피200 | 7.0% | 22% | 1990–2024 |
| 3 | 선진국 ex-US (MSCI EAFE) | 6.0% | 18% | 1990–2024 |
| 4 | 신흥국 (MSCI EM) | 8.0% | 23% | 1995–2024 |
| 5 | 한국채(3y) | 3.4% | 3% | 2000–2024 |
| 6 | 미국채(10y, KRW) | 4.5% | 10% | 1990–2024 |
| 7 | 금 (KRW) | 7.0% | 17% | 1990–2024 |
| 8 | 달러 (USD/KRW) | 1.2% | 10% | 1997–2024 |
| 9 | 원화 현금 (CD 1y) | 2.5% | 0.1% | 2000–2024 |
| 10 | 비트코인 (KRW) | 45% | 75% | 2014–2024 (fat-tail 미반영) |

상관행렬은 11×11 stylized facts (예: 주식군 내부 0.55–0.90, 주식 vs USD/KRW −0.30, 주식 vs 채권 ≈ 0). Cholesky 분해 시 PD가 깨지면 자동 jitter 보정.

### 다자산 GBM

주 단위 (`dt = 1/52`). Cholesky 인수 L을 통해 상관된 충격 z = Lε 생성.

```
S_i(t+1) = S_i(t) · exp((μ_i − σ_i²/2)·dt + σ_i·√dt · z_i)
V(t)     = S0 · Σ_i w_i · S_i(t)/S_i(0)        # 매수후 보유, 리밸런싱 없음
```

250 경로 시뮬레이션 → 최종값 분포의 10퍼센타일에 가장 가까운 경로를 "stress path"로 선정.

### 경기 4국면 (Bridgewater All-Weather 차용)

| 국면 | 성장 | 인플레 | 강세 자산 | 약세 자산 |
|---|---|---|---|---|
| 🌱 회복기 (Reflation) | ↑ | ↓ | 신흥국, 회사채, 비트코인 | 금, USD, 방어주 |
| ☀️ 확장기 (Goldilocks) | ↑↑ | ↔ | S&P500, 나스닥, 선진국 | 금, 안전자산 |
| 🔥 호황기 (Late/Inflation) | ↑ | ↑↑ | 금, 원자재, 단기채 | 장기채, 성장주 |
| ❄️ 침체기 (Recession) | ↓ | ↑ or ↓ | 미국채, 금, USD | 거의 모든 주식, BTC |

시뮬레이션 시작 시 4국면 중 균등 랜덤 선택. 26주마다 마르코프 전이 (유지 30%, 인접 50%, 점프 20%). 결정 패널 등장 시점에 현재 국면이 표시되고, 그 국면에 맞는 뉴스 풀에서 헤드라인 선정.

### 뉴스 풀

11자산 × 4국면 × 5건 ≈ 220건의 한국 경제지 톤 헤드라인. 결정 시점에 포트폴리오에서 가장 많이 하락한 자산 + 현재 국면을 매칭해 뉴스 풀에서 랜덤 선택. 손실 -25% 이상에선 "LIVE" 깜빡임 + shake 애니메이션으로 패닉 분위기 강화.

### 결정 회계

```
units (포트 단위 수, 시작 1.0), cashKRW (매도 후 현금), totalIn (총 투입금)
hold:  변화 없음
buy:   units += S0 / V(t),  totalIn += S0
sell:  cashKRW = units * V(t),  units = 0,  이후 cashKRW 연 2.5%로 복리 성장

final  = (units * V(T)) + cashKRW
return = (final - totalIn) / totalIn
```

매도 후에도 시뮬레이션은 끝까지 진행되며 결과 패널에서 "끝까지 보유했더라면" 비교 표시 — 후회 학습.

## 프로젝트 구조

```
seneca/
├── index.html                              # 메인 앱 (자기충족, ~75KB)
├── README.md                               # 이 문서
├── seneca.jpg                              # 원본 마스코트 일러스트
├── assets/
│   ├── build_logo.py                       # JPG → 투명 PNG·favicon 빌드 스크립트
│   ├── logo.png                            # topbar 로고 (투명 배경)
│   ├── favicon-32.png                      # 32×32 표준 탭 아이콘
│   ├── favicon-180.png                     # 180×180 Apple touch icon
│   └── favicon.ico                         # 16/32/48 멀티 해상도
└── montecarlo_stress_test_simulator.html   # v1 (참고용, deprecated)
```

`seneca.jpg`를 갱신하면 `python assets/build_logo.py`로 favicon 세트를 재생성.

## 면책 / 한계

- **투자 자문이 아닙니다.** 교육·심리훈련 도구.
- μ/σ는 historical long-run averages 기반의 추정치이며, 실제 미래 수익률은 모델과 크게 다를 수 있습니다.
- GBM은 비트코인의 fat-tail (특히 -50% 이상의 단기 폭락)을 과소평가합니다.
- 인플레이션·세금·거래비용은 미반영. 명목수익률 기준.
- 리밸런싱은 미반영 (buy-and-hold 가정).

## 향후

- 분기/연 리밸런싱 토글
- 비트코인 jump-diffusion 또는 Student-t 마진
- 실제 시계열 부트스트랩 옵션
- 사용자 결정 패턴 통계 (서버리스 익명 집계)


---

seneca v2 · [jumpingkoala](https://jumpingkoala.com/)
