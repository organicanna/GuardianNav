# src/guardiannav/agent.py
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Literal

Intent = Literal["YES", "NO", "SILENCE", "CANCEL", "UNKNOWN"]

@dataclass
class Motion:
    speed_mps: float = 0.0
    drift_m: float = 0.0

@dataclass
class AgentConfig:
    static_speed_max: float = 0.5       # m/s
    static_window_s: int = 300          # 5 minutes
    deviation_min_m: float = 75         # pas encore utilisé (route)
    voice_silence_window_s: int = 30
    escalation_countdown_s: int = 600   # 10 minutes

class GuardianAgent:
    """
    Agent minimal: surveille la "vitesse" fournie par une source (callback),
    déclenche une alerte si vitesse <= seuil pendant ≥ static_window_s,
    puis gère une interaction basique (oui/non/silence/cancel).
    """

    def __init__(self, get_motion_cb, speak_cb=None, notify_cb=None, call_contacts_cb=None, config: Optional[AgentConfig]=None):
        self.get_motion_cb = get_motion_cb
        self.speak_cb = speak_cb or (lambda msg: print(f"[VOICE] {msg}"))
        self.notify_cb = notify_cb or (lambda title, body: print(f"[NOTIF] {title}: {body}"))
        self.call_contacts_cb = call_contacts_cb or (lambda: print("[CALL] Appel contacts d’urgence"))
        self.cfg = config or AgentConfig()

        self._static_start: Optional[float] = None
        self._escalation_deadline: Optional[float] = None

    def _now(self) -> float:
        return time.time()

    def tick(self) -> dict:
        """Une itération de boucle; retourne un état JSON-ifiable."""
        motion: Motion = self.get_motion_cb()
        now = self._now()

        # 1) Détection "statique > 5 min"
        if motion.speed_mps <= self.cfg.static_speed_max:
            if self._static_start is None:
                self._static_start = now
            static_elapsed = now - self._static_start
        else:
            # mouvement repris => reset
            self._static_start = None
            self._escalation_deadline = None
            return {
                "state": "IDLE",
                "reason": "Mouvement détecté, reprise normale",
                "user_motion": motion.__dict__,
            }

        if self._static_start and (now - self._static_start) >= self.cfg.static_window_s:
            # 2) Phase d’assistance
            self.notify_cb("Vérification sécurité", "Êtes-vous en sécurité ?")
            self.speak_cb("Allez-vous bien ? (répondez: oui / non / j'annule)")
            intent = self._listen_once(timeout_s=self.cfg.voice_silence_window_s)

            if intent == "YES":
                self._escalation_deadline = None
                self._static_start = now  # on repousse la fenêtre (suspendre 15 min si tu veux)
                return {
                    "state": "IDLE",
                    "reason": "Utilisateur a confirmé que tout va bien",
                    "user_motion": motion.__dict__,
                }
            elif intent == "NO":
                # assistance minimale; ici on se contente d’annoncer et de préparer escalade
                self.speak_cb("Je reste avec vous. Dites 'j'annule' pour arrêter. J’appellerai un contact d’urgence si vous ne bougez pas.")
                self._escalation_deadline = now + self.cfg.escalation_countdown_s
                return {
                    "state": "ASSIST",
                    "reason": "Demande d’aide détectée",
                    "user_motion": motion.__dict__,
                    "timers": {"escalation_deadline_epoch": self._escalation_deadline},
                }
            elif intent == "CANCEL":
                self._escalation_deadline = None
                return {
                    "state": "CANCELLED",
                    "reason": "Utilisateur a annulé",
                    "user_motion": motion.__dict__,
                }
            else:
                # SILENCE ou UNKNOWN -> préparer escalade
                if self._escalation_deadline is None:
                    self.speak_cb("Je n’ai pas entendu. J’appellerai votre contact d’urgence dans 10 minutes sauf si vous dites 'j'annule' ou si vous repartez.")
                    self._escalation_deadline = now + self.cfg.escalation_countdown_s
                return {
                    "state": "ESCALATE",
                    "reason": "Silence ou réponse inconnue",
                    "user_motion": motion.__dict__,
                    "timers": {"escalation_deadline_epoch": self._escalation_deadline},
                }

        # 3) Escalade si délai dépassé et toujours statique
        if self._escalation_deadline and now >= self._escalation_deadline:
            self.call_contacts_cb()
            # éviter répétition
            self._escalation_deadline = None
            return {
                "state": "CALL_CONTACTS",
                "reason": "Inactivité prolongée sans annulation",
                "user_motion": motion.__dict__,
            }

        return {
            "state": "IDLE",
            "reason": "Statique mais fenêtre non atteinte",
            "user_motion": motion.__dict__,
            "static_elapsed_s": int((now - self._static_start) if self._static_start else 0),
        }

    # --- I/O simples (à remplacer plus tard par micro/reconnaissance) ---
    def _listen_once(self, timeout_s: int) -> Intent:
        """
        Version terminal : attend une saisie utilisateur pendant timeout_s.
        Tape 'oui', 'non', 'j'annule' pour simuler.
        """
        print(f"[INPUT] Répondez dans {timeout_s}s (oui / non / j'annule). Appuyez Entrée pour silence.")
        start = self._now()
        # Lecture bloquante simple; pour un vrai timeout, on remplacerait par I/O non bloquante.
        try:
            user = input().strip().lower()
        except EOFError:
            user = ""
        if (self._now() - start) > timeout_s:
            return "SILENCE"
        if user in ("oui", "o", "yes", "ok", "ça va", "ca va"):
            return "YES"
        if user in ("non", "no", "besoin d'aide", "aidez-moi", "aide"):
            return "NO"
        if user in ("j'annule", "annule", "cancel"):
            return "CANCEL"
        return "SILENCE" if user == "" else "UNKNOWN"


def main():
    # Source de mouvement de démo: vitesse constante lue depuis une variable mutable
    speed_state = {"v": 0.0}  # 0 = statique; change à 1.2 pour simuler une reprise

    def get_motion():
        return Motion(speed_mps=speed_state["v"], drift_m=0.0)

    agent = GuardianAgent(get_motion_cb=get_motion)

    print("[GuardianNav] Démarrage (démo). Tape '1' + Entrée pour simuler une marche (>1 m/s).")
    started = time.time()
    while True:
        state = agent.tick()
        print(state)
        # petite “console” pour changer la vitesse
        try:
            if speed_state["v"] <= 0.5 and (time.time() - started) % 5 < 0.1:
                print("Astuce: tapez '1' puis Entrée pour simuler que vous repartez.")
            line = None
            # input non bloquant serait mieux; ici, lecture occasionnelle:
            if state["state"] in ("IDLE", "ESCALATE", "ASSIST"):
                # Offre la possibilité de saisir une commande de vitesse
                pass
            # Micro-sommeil
            time.sleep(1)
            # lecture optionnelle
            # (pour simplifier, on ne lit pas à chaque tick; utilisez l’invite de _listen_once)
        except KeyboardInterrupt:
            print("\n[GuardianNav] Arrêt.")
            break

