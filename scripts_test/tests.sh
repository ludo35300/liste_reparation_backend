#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  Liste Réparation — Menu de tests pytest
# ─────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

clear

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║     Liste Réparation — Tests         ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${RESET}"
}

print_menu() {
    echo -e "${BOLD}  Que veux-tu faire ?${RESET}\n"
    echo -e "  ${GREEN}1${RESET})  Lancer tous les tests"
    echo -e "  ${GREEN}2${RESET})  Tests + couverture (terminal)"
    echo -e "  ${GREEN}3${RESET})  Tests + rapport HTML"
    echo -e "  ${GREEN}4${RESET})  Rejouer uniquement les tests en échec"
    echo -e "  ${YELLOW}5${RESET})  Tester un fichier précis"
    echo -e "  ${YELLOW}6${RESET})  Tester un service précis"
    echo -e "  ${YELLOW}7${RESET})  Tester un controller précis"
    echo -e "  ${RED}0${RESET})  Quitter\n"
}

run_pytest() {
    echo -e "\n${CYAN}▶ $1${RESET}\n"
    eval "$2"
    STATUS=$?
    echo ""
    if [ $STATUS -eq 0 ]; then
        echo -e "${GREEN}${BOLD}  ✔ Tous les tests sont passés${RESET}"
    else
        echo -e "${RED}${BOLD}  ✘ Des tests ont échoué${RESET}"
    fi
}

choisir_fichier() {
    local DOSSIER=$1
    echo -e "\n${BOLD}  Fichiers disponibles dans ${DOSSIER} :${RESET}\n"
    FILES=($(find "$DOSSIER" -name "test_*.py" | sort))
    if [ ${#FILES[@]} -eq 0 ]; then
        echo -e "  ${RED}Aucun fichier trouvé.${RESET}\n"
        return 1
    fi
    for i in "${!FILES[@]}"; do
        echo -e "  ${GREEN}$((i+1))${RESET})  ${FILES[$i]}"
    done
    echo ""
    read -p "  Ton choix (numéro) : " CHOIX
    if [[ "$CHOIX" =~ ^[0-9]+$ ]] && [ "$CHOIX" -ge 1 ] && [ "$CHOIX" -le "${#FILES[@]}" ]; then
        run_pytest "Test : ${FILES[$((CHOIX-1))]}" "pytest ${FILES[$((CHOIX-1))]} -v"
    else
        echo -e "  ${RED}Choix invalide.${RESET}"
    fi
}

while true; do
    print_header
    print_menu
    read -p "  Ton choix : " CHOIX
    echo ""

    case "$CHOIX" in
        1) run_pytest "Tous les tests" "pytest tests/ -v" ;;
        2) run_pytest "Tests + couverture terminal" "pytest tests/ --cov=app --cov-report=term-missing -v" ;;
        3) run_pytest "Tests + rapport HTML" "pytest tests/ --cov=app --cov-report=html -v"
           echo -e "  ${CYAN}→ Ouvre htmlcov/index.html dans Firefox${RESET}" ;;
        4) run_pytest "Tests en échec seulement" "pytest tests/ -v --lf" ;;
        5) choisir_fichier "tests" ;;
        6) choisir_fichier "tests/test_services" ;;
        7) choisir_fichier "tests/test_controllers" ;;
        0) echo -e "  ${CYAN}À bientôt !${RESET}\n" ; exit 0 ;;
        *) echo -e "  ${RED}Choix invalide, réessaie.${RESET}" ;;
    esac

    echo ""
    read -p "  Appuie sur Entrée pour revenir au menu..."
    clear
done