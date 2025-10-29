
INSERT INTO events (
    id, title, description, end_date, active, liquidity, volume,
    volume24hr, liquidity_clob, resolution_source, is_financial,
    is_crypto, is_big_event, is_excluded
) VALUES
(23246, 'New York City Mayoral Election', 'The 2025 New York City mayoral election will be held on November 4, 2025.

This market will resolve according to the candidate wins the election.

The primary resolution source for this market will be a consensus of credible reporting, however if there is any ambiguity in the results this market will resolve according to official information from New York City.


', '2025-11-04T12:00:00+00:00', True, 23211932.3882, 321800613.694084, 9683340.691288998, 23211932.3882, '', False, True, True, False),
(30829, 'Democratic Presidential Nominee 2028', 'This market will resolve to “Yes” if the named individual wins and accepts the 2028 nomination of the Democratic Party for U.S. president. Otherwise, this market will resolve to “No”.

The resolution source for this market will be a consensus of official Democratic Party sources.

Any replacement of the democratic nominee before election day will not change the resolution of the market.', '2028-11-07T00:00:00+00:00', True, 14332416.02935, 246511439.035842, 5641712.317933, 14332416.02935, '', False, True, True, False),
(27824, 'Fed decision in October?', 'The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.

This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve''s October 2025 meeting.

If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there''s a cut/increase of 12.5 bps it will be considered to be 25 bps)

The resolution source for this market is the FOMC’s statement after its meeting scheduled for October 28 - 29, 2025 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.

This market may resolve as soon as the FOMC’s statement for their October meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket.
', '2025-10-29T12:00:00+00:00', True, 6035075.06672, 114518101.845431, 27657198.966401014, 12463977.1909, '', True, True, True, False),
(31552, 'Presidential Election Winner 2028', 'The 2028 US Presidential Election is scheduled to take place on November 7, 2028.

This market will resolve to the person who wins the 2028 US Presidential Election. Otherwise, this market will resolve to “No.”

The resolution source for this market is the Associated Press, Fox News, and NBC. This market will resolve once all three sources call the race for the same candidate. If all three sources haven’t called the race for the same candidate by the inauguration date (January 20, 2029) this market will resolve based on who is inaugurated.', '2028-11-07T00:00:00+00:00', True, 8944729.73308, 99193441.272257, 1976114.776585, 8944729.73308, '', False, True, True, False),
(31875, 'Republican Presidential Nominee 2028', 'This market will resolve to “Yes” if the named individual wins and accepts the 2028 nomination of the Republican Party for U.S. president. Otherwise, this market will resolve to “No”.

The resolution source for this market will be a consensus of official Republican Party sources.

Any replacement of the Republican nominee before election day will not change the resolution of the market.', '2028-11-07T00:00:00+00:00', True, 4186686.12649, 66347692.730253, 1401813.469635, 4186686.12649, '', False, True, True, False),
(26857, 'Xi Jinping out in 2025?', 'This market will resolve to "Yes" if China''s General Secretary of the Communist Party, Xi Jinping, is removed from power for any length of time between June 12 and December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

CCP General Secretary Xi Jinping will be considered removed from power if he announces his resignation from his role as General Secretary, or is otherwise dismissed, detained, disqualified, or otherwise loses his position or is prevented from fulfilling his duties as General Secretary within this market''s timeframe.

The primary resolution source for this market will be a consensus of credible reporting.', '2025-12-31T23:55:00+00:00', True, 843371.75748, 44626955.81028, 1095833.8737980025, 843371.75748, '', False, True, True, False),
(16096, 'What price will Bitcoin hit in 2025?', 'This is a market group over whit prices Bitcoin will hit in 2025.', '2026-01-01T05:00:00+00:00', True, 1011272.38609, 39127725.281901, 617255.7866979999, 1011272.38609, '', True, True, False, False),
(52525, 'What price will Bitcoin hit in October?', 'What price will Bitcoin hit in October?', '2025-11-01T04:00:00+00:00', True, 999669.25777, 39095805.508074, 1888379.6541510003, 999669.25777, '', True, True, False, False),
(16097, 'What price will Ethereum hit in 2025?', 'This is a market group over what prices Ethereum will hit in 2025.', '2026-01-01T05:00:00+00:00', True, 671500.32363, 27251754.906498, 258318.89522200002, 671500.32363, '', True, True, False, False),
(16108, 'Russia x Ukraine ceasefire in 2025?', 'This market will resolve to "Yes" if there is an official ceasefire agreement, defined as a publicly announced and mutually agreed halt in military engagement, between Russia and Ukraine by December 31, 2025, 11:59 PM ET.

If the agreement is officially reached before the resolution date, this market will resolve to "Yes," regardless of whether the ceasefire officially starts afterward.

Any form of informal agreement will not be considered an official ceasefire. Humanitarian pauses will not count toward the resolution of this market.

This market''s resolution will be based on official announcements from both Russia and Ukraine; however, a wide consensus of credible media reporting stating an official ceasefire agreement between Russia and Ukraine has been reached will suffice.', '2025-12-31T12:00:00+00:00', True, 414519.5506, 24627439.189134, 96091.59701299996, 414519.5506, '', True, True, True, False),
(52528, 'What price will Ethereum hit in October?', 'What price will Ethereum hit in October?', '2025-11-01T04:00:00+00:00', True, 559453.9081, 24062892.555208, 1040744.524259, 559453.9081, '', True, True, False, False),
(16085, 'How many Fed rate cuts in 2025?', 'This is a market group over how many Fed rate cuts will happen in 2025.', '2025-12-31T12:00:00+00:00', True, 1220085.47014, 21206223.64076, 151436.29170600002, 1220085.47014, '', True, False, False, False),
(17505, 'Jerome Powell out as Fed Chair in 2025?', 'This market will resolve to “Yes” if Jerome Powell ceases to be the Chair of the U.S. Federal Reserve for any period of time between January 26, 2025 ET and December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to “No”.

The resolution source for this market will be information from the U.S. Government however a consensus of credible reporting will also suffice.
', '2025-12-31T12:00:00+00:00', True, 109211.65667, 10624707.763657, 26724.503498, 109211.65667, '', True, True, False, False),
(16092, 'US recession in 2025?', 'This market will resolve to “Yes”, if either of the following conditions are met:

1.  The National Bureau of Economic Research (NBER) publicly announces that a recession has occurred in the United States, at any point in 2025, with the announcement made by December 31, 2025, 11:59 PM ET.

2.  The seasonally adjusted annualized percent change in quarterly U.S. real GDP from the previous quarter is less than 0.0 for two consecutive quarters between Q4 2024 and Q4 2025 (inclusive), as reported by the Bureau of Economic Analysis (BEA). 

Otherwise, this market will resolve to "No". 

Note that advance estimates will be considered. For example, if upon release, the advance estimate for Q2 2025 was negative, and the Q1 2025''s most recent, up-to-date estimate was also negative, this market would resolve to "Yes". If on December 31, 2025 the latest estimate for quarterly GDP in Q3 2025 was negative, this market will stay open until the Advance estimate of Q4 2025 is published, at which point it will resolve to "Yes" if Q4 2025 was negative or if the NBER declares a recession by then.

The resolution source will be the official announcements from the NBER and the BEA’s estimate of seasonally adjusted annualized percent change in quarterly US real GDP from previous quarters as released by the Bureau of Economic Analysis (BEA), https://www.bea.gov/data/gdp/gross-domestic-product', '2026-02-28T12:00:00+00:00', True, 93626.837, 9877789.954292, 5767.478332000001, 93626.837, '', True, True, True, False),
(39671, 'Lisa Cook out as Fed Governor by...?', 'This market will resolve to “Yes” if Lisa Cook announces her resignation or otherwise ceases to be a member of the Federal Reserve Board of Governors for any period of time between August 25, and September 30, 2025, 11:59 PM ET. Otherwise, this market will resolve to “No”.

Only official announcements of Cook''s resignation or removal made before her term is scheduled to end, made by either Cook or the Board of Governors, will qualify. Announcements from Trump or his administration will not alone qualify. 

Temporary absences or attempts at termination which do not actually remove Cook from the Board of Governors of the Federal Reserve will not qualify. 

The resolution source for this market will be information from the U.S. Government however a consensus of credible reporting will also suffice.', '2025-12-31T00:00:00+00:00', True, 54862.92004, 9764671.738258, 7410.163104, 54862.92004, '', True, True, True, False),
(38884, 'US x Venezuela military engagement by...?', 'This market will resolve to "Yes" if there is a military engagement between the military forces of the United States of America and Venezuela between August 21, and October 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

A "military engagement" is defined as any incident involving the use of force such as missile strikes, artillery fire, exchange of gunfire, or other forms of direct military engagement between US and Venezuelan military forces. Non-violent actions, such as warning shots, artillery fire into uninhabited areas, or missile launches that land in territorial waters or pass through airspace, will not qualify for a "Yes" resolution. Intentional ship ramming that results in significant damage to (e.g., a hole in the hull) or the sinking of a military ship by another will count toward a "Yes" resolution; however, minor damage (scrapes, dents) will not. Any U.S. military kinetic strike that impacts Venezuelan land territory will qualify for a “Yes” resolution.

Missiles or drones which are intercepted and surface-to-air missile strikes will not be sufficient for a "Yes" resolution, regardless of whether they land on adversarial territory or cause damage.

Note: the U.S. Coast Guard is a branch of the U.S. Armed Forces; Venezuela’s Milicia Nacional Bolivariana (militia) is a “special component” of the Venezuelan National Bolivarian Armed Forces (FANB); and Venezuela’s Coast Guard (Comando de Guardacostas) is a component of the Venezuelan Navy (Armada Bolivariana) and thus part of the FANB.

The resolution source for this market will be a consensus of credible reporting.', '2025-10-31T00:00:00+00:00', True, 169543.49123, 8959430.774823, 194204.60950699996, 169543.49123, '', True, True, True, False),
(16105, 'Khamenei out as Supreme Leader of Iran in 2025?', 'This market will resolve to "Yes" if Iran''s Supreme leader, Ali Khamenei, is removed from power for any length of time between December 28, 2024, and December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

Khamenei will be considered to be removed from power if he resigns, is detained, or otherwise loses his position or is prevented from fulfilling his duties as Supreme Leader of Iran within this market''s timeframe.

The primary resolution source for this market will be a consensus of credible reporting.', '2025-12-31T12:00:00+00:00', True, 125546.5631, 7793793.94971, 23292.5029, 125546.5631, '', False, True, True, False),
(22987, 'Who will Trump pardon in 2025?', 'This market will resolve to "Yes" if the listed individual receives a presidential pardon, commutation, or reprieve from Donald Trump by December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

The primary resolution source for whether the individual is pardoned or not will be official information from the US government, however a consensus of credible reporting will also be used.', '2025-12-31T12:00:00+00:00', True, 235798.71506, 7183009.826226, 77341.47797100003, 235798.71506, '', True, True, True, False),
(33495, 'Will Trump meet with Xi Jinping by October 31?', 'This market will resolve to "Yes" if Donald Trump meets with Xi Jinping between July 21, and October 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

An exchange of words, handshake, direct conversation, or other clear personal interaction between the named individuals will qualify as a meeting. Merely standing in proximity, making eye contact, or being present in the same room or event without direct interaction will not qualify.

A meeting is defined as any encounter where both listed individual and Trump are present and interact with each other in person.

The resolution source will be a consensus of credible reporting.', '2025-10-31T00:00:00+00:00', True, 290442.90554, 6782949.503492, 1156525.8613440036, 290442.90554, '', False, True, True, False),
(17413, 'Will China invade Taiwan in 2025?', 'This market will resolve to "Yes" if China commences a military offensive intended to establish control over any portion of the Republic of China (Taiwan) by December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".

Territory under the administration of the Republic of China including any inhabited islands will qualify, however uninhabited islands will not qualify. 

The resolution source for this market will be will be official confirmation by China, Taiwan, the United Nations, or any permanent member of the UN Security Council, however a consensus of credible reporting will also be used.', '2025-12-31T12:00:00+00:00', True, 159498.24625, 6771323.193366, 58944.82151499999, 159498.24625, '', False, True, True, False),
(16817, 'Which countries will Donald Trump visit in 2025?', 'If U.S. President Donald Trump visits a listed country between January 15 and December 31, 2025 11:59 PM ET, the relevant market will resolve to "Yes". Otherwise, this market will resolve to "No".

For the purpose of this market, a "visit" is defined as Trump physically entering the terrestrial or maritime territory of the listed country. Whether or not Trump enters the country''s airspace during the timeframe of this market will have no bearing on a positive resolution.

The primary resolution source for this information will be official information from government of the United States of America, official information from Trump or released by his verified social media accounts (e.g. https://twitter.com/POTUS), however, a consensus of credible reporting will also be used.
', '2025-12-31T12:00:00+00:00', True, 64364.68022, 6172441.521396, 28486.381317999996, 64364.68022, '', True, True, True, False),
(26863, ' 2nd Place in New York City Mayoral Election', 'The 2025 New York City mayoral election will be held on November 4, 2025, to elect the mayor of New York City.

This market will resolve according to the candidate candidate that wins the second most votes in this election.

The primary resolution source for this market will be a consensus of credible reporting, however if there is any ambiguity in the results this market will resolve according to official information from New York City.', '2025-11-04T23:55:00+00:00', True, 1205499.38857, 5715974.509, 176060.272599, 1205499.38857, '', False, True, True, False),
(33526, 'Will Polymarket US go live in 2025?', 'This market will resolve to "Yes" if a real-money trade is publicly placed on a regulated, Polymarket-operated Designated Contract Market (DCM) by December 31, 2025, at 11:59 PM ET. Otherwise, this market will resolve to "No."

The resolution source will be a consensus of credible reporting.', '2025-12-31T00:00:00+00:00', True, 127039.30405, 5425883.371953, 381105.748577, 127039.30405, '', False, True, False, False),
(35908, 'Who will Trump nominate as Fed Chair?', 'This market will resolve according to the next individual Donald Trump, as President of the United States, formally nominates to be Chair of the Federal Reserve by December 31, 2026, 11:59 PM ET. 

Formal nominations are defined as the submission of a nomination message to the U.S. Senate.

Acting or interim appointments will not count unless the individual is formally nominated to be Chair of the Federal Reserve by submission of a nomination message to the U.S. Senate.

The primary resolution source for this market will be official information from the U.S. Senate (see: https://www.senate.gov/legislative/nominations_new.htm), however a consensus of credible reporting may also be used.
', '2026-12-31T00:00:00+00:00', True, 398136.29256, 5166763.774826, 141504.892088, 398136.29256, '', True, True, True, False),
(38010, 'Will Trump meet with Putin again by...?', 'On August 15, 2025, U.S. President Donald Trump and Russian President Vladimir Putin met in person at Joint Base Elmendorf-Richardson near Anchorage, Alaska, for a summit focused on potential peace terms in Ukraine. 

This market will resolve to "Yes" if Vladimir Putin meets with Donald Trump on a separate occasion from the August 15, 2025 meeting by December 31, 2025, 11:59 PM ET.  Otherwise, this market will resolve to "No".

Encounters that are part of, or a continuation of, the August 15 meeting will not qualify, even if they occur on a different day (e.g. August 16).

A meeting is defined as any encounter where both Putin and Trump are present and interact with each other in person.

The resolution source will be a consensus of credible reporting.', '2025-12-31T00:00:00+00:00', True, 89734.17157, 5120548.276854, 63805.671258999995, 89734.17157, '', False, True, True, False),
(35090, 'Fed decision in December?', 'The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.

This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve''s December 2025 meeting.

If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there''s a cut/increase of 12.5 bps it will be considered to be 25 bps)

The resolution source for this market is the FOMC’s statement after its meeting scheduled for December 9 - 10, 2025 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.

This market may resolve as soon as the FOMC’s statement for their December meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket.
', '2025-12-10T00:00:00+00:00', True, 392814.5376, 5081424.700732, 1003791.8900609988, 392814.5376, '', True, True, True, False)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    end_date = EXCLUDED.end_date,
    active = EXCLUDED.active,
    liquidity = EXCLUDED.liquidity,
    volume = EXCLUDED.volume,
    volume24hr = EXCLUDED.volume24hr,
    liquidity_clob = EXCLUDED.liquidity_clob,
    resolution_source = EXCLUDED.resolution_source,
    is_financial = EXCLUDED.is_financial,
    is_crypto = EXCLUDED.is_crypto,
    is_big_event = EXCLUDED.is_big_event,
    is_excluded = EXCLUDED.is_excluded,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO markets (
    id, event_id, question, end_date, liquidity, volume, volume24hr,
    outcomes, outcome_prices, active, description
) VALUES
(1, 27824, 'Fed decreases interest rates by 50+ bps after October 2025 meeting?', '2025-10-29T12:00:00+00:00', 2482410.74458, 40446604.940503, 8757785.210175028, '"[\"Yes\", \"No\"]"', '"[\"0.0045\", \"0.9955\"]"', True, 'The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.

This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve''s October 2025 meeting.

If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there''s a cut/increase of 12.5 bps it will be considered to be 25 bps)

The resolution source for this market is the FOMC’s statement after its meeting scheduled for October 28 - 29, 2025 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.

This market may resolve as soon as the FOMC’s statement for their October meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket.'),
(2, 27824, 'Fed decreases interest rates by 25 bps after October 2025 meeting?', '2025-10-29T12:00:00+00:00', 1438679.73062, 39865836.011053, 7502589.8799239835, '"[\"Yes\", \"No\"]"', '"[\"0.982\", \"0.018\"]"', True, 'The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.

This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve''s October 2025 meeting.

If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there''s a cut/increase of 12.5 bps it will be considered to be 25 bps)

The resolution source for this market is the FOMC’s statement after its meeting scheduled for October 28 - 29, 2025 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.

This market may resolve as soon as the FOMC’s statement for their October meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket.'),
(3, 27824, 'No change in Fed interest rates after October 2025 meeting?', '2025-10-29T12:00:00+00:00', 2113984.59152, 34205660.893875, 8360040.816302002, '"[\"Yes\", \"No\"]"', '"[\"0.013\", \"0.987\"]"', True, 'The FED interest rates are defined in this market by the upper bound of the target federal funds range. The decisions on the target federal fund range are made by the Federal Open Market Committee (FOMC) meetings.

This market will resolve to the amount of basis points the upper bound of the target federal funds rate is changed by versus the level it was prior to the Federal Reserve''s October 2025 meeting.

If the target federal funds rate is changed to a level not expressed in the displayed options, the change will be rounded up to the nearest 25 and will resolve to the relevant bracket. (e.g. if there''s a cut/increase of 12.5 bps it will be considered to be 25 bps)

The resolution source for this market is the FOMC’s statement after its meeting scheduled for October 28 - 29, 2025 according to the official calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

The level and change of the target federal funds rate is also published at the official website of the Federal Reserve at https://www.federalreserve.gov/monetarypolicy/openmarket.htm.

This market may resolve as soon as the FOMC’s statement for their October meeting with relevant data is issued. If no statement is released by the end date of the next scheduled meeting, this market will resolve to the "No change" bracket.')
ON CONFLICT (id) DO UPDATE SET
    event_id = EXCLUDED.event_id,
    question = EXCLUDED.question,
    end_date = EXCLUDED.end_date,
    liquidity = EXCLUDED.liquidity,
    volume = EXCLUDED.volume,
    volume24hr = EXCLUDED.volume24hr,
    outcomes = EXCLUDED.outcomes,
    outcome_prices = EXCLUDED.outcome_prices,
    active = EXCLUDED.active,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO data_sync_log (
    total_events, total_volume, total_liquidity, financial_events,
    crypto_events, politics_war_events, high_volume_events, sync_status
) VALUES (
    26,
    1267635321.079638,
    72375733.83129,
    15,
    25,
    19,
    26,
    'success'
);


SELECT * FROM events_with_market_stats ORDER BY volume DESC;

SELECT * FROM high_volume_events;

SELECT * FROM active_events_recent;

SELECT * FROM events WHERE is_financial = true AND active = true ORDER BY volume DESC;

SELECT * FROM events WHERE is_crypto = true AND active = true ORDER BY volume DESC;

SELECT * FROM events WHERE is_big_event = true AND active = true ORDER BY volume DESC;