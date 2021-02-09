import numpy as np
import matplotlib.pyplot as plt

from load import get_participant_data
from confusion import ConfusionMatrix
from util import get_participants_responses
from sensitivity import get_interstim_sensitivities, log_fit_sensitivities

participants_c20_s20 = get_participant_data(slowdown=20, compensation=20)
participants_c20_s1 = get_participant_data(slowdown=20, compensation=1)

responses_c20_s20 = get_participants_responses(participants_c20_s20)
responses_c20_s1 = get_participants_responses(participants_c20_s1)

confusion_c20_s20 = ConfusionMatrix.of_indices(responses_c20_s20)
confusion_c20_s1 = ConfusionMatrix.of_indices(responses_c20_s1)

# fig, (left, right) = plt.subplots(1, 2)
# left.set_title("s=20, c=1")
# right.set_title("s=20, c=20")
# left.imshow(confusion_c20_s1.totals)
# right.imshow(confusion_c20_s20.totals)
# plt.show()

labels = ["c=1", "c=20"]
colors = ["tab:orange", "tab:blue", "tab:green"]
markers = ["o", "*", "x"]
for idx, cm in enumerate((confusion_c20_s1, confusion_c20_s20)):
    color = colors[idx]
    marker = markers[idx]
    label = labels[idx]
    s = get_interstim_sensitivities(cm)
    x, y = log_fit_sensitivities(s)
    plt.plot(x, y, color=color, label=f"{label} (log)")
    plt.plot(*zip(*s), color=color, marker=marker, linestyle="None", label=label)
plt.xlabel("Interstim distance (positions)")
plt.ylabel("Sensitivity index (d')")
plt.legend(loc="lower right")
plt.show()