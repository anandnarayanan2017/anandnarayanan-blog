A rule can block a sign-in. A model can only raise its hand.

IAM AI scores every Entra ID sign-in from 0 to 100:

score = rules × 0.55 + anomaly models × 0.45

Two lines matter more than the weights:

→ If any single rule contributes 60 or more, the score is at least 71: BLOCK, whatever the models say.
→ With no rule fired, the score can never exceed 45. The models can never block on their own.

So every block traces back to a rule with a sentence attached, like “Refresh token replayed 3 times”.

The most consequential bug was one character long. The code assumed lower anomaly scores meant more unusual. The
library uses the opposite convention. For 45% of every score, the scale was upside down, and nothing failed,
because the hard rules still blocked the obvious attacks.

Part 2 of the IAM AI series, with the eleven rules and the arithmetic, is in the first comment.

#IdentitySecurity #MachineLearning #AnomalyDetection #SoftwareArchitecture #RegTech
