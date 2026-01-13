#!/usr/bin/env bash
set -euo pipefail

# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
if ! command -v conda &> /dev/null; then
    echo "[INFO] Conda가 발견되지 않았습니다. Miniconda를 설치합니다..."

    INSTALLER="miniconda.sh"
    URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    CONDA_DIR="$HOME/miniconda"

    if command -v wget >/dev/null 2>&1; then
        wget -q "$URL" -O "$INSTALLER"
    elif command -v curl >/dev/null 2>&1; then
        curl -fsSL "$URL" -o "$INSTALLER"
    else
        echo "[ERROR] wget 또는 curl이 필요합니다(다운로드 불가)."
        exit 1
    fi

    bash "$INSTALLER" -b -u -p "$CONDA_DIR"
    rm -f "$INSTALLER"

    # conda 활성화를 위해 conda.sh 로드
    # shellcheck disable=SC1091
    source "$CONDA_DIR/etc/profile.d/conda.sh"

    # 약관 자동 수락(지원 안 하면 무시)
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r    2>/dev/null || true
else
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi

# Conda 환경 생성 및 활성화
# 'myenv'라는 이름의 환경이 없을 경우 생성
if ! conda env list | awk '{print $1}' | grep -qx "myenv"; then
    echo "[INFO] myenv 가상환경을 생성합니다..."
    conda create -n myenv python=3.10 -y
fi
conda activate myenv

## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1
fi

# 필요한 패키지 설치
python -m pip install -U pip >/dev/null
python -m pip install mypy >/dev/null

# output 디렉토리 생성 (없을 경우)
mkdir -p output

# Submission 폴더 파일 실행
cd submission || { echo "[ERROR] submission 디렉토리로 이동 실패"; exit 1; }

# submission 폴더 내 python 파일이 없으면 실패
shopt -s nullglob
py_files=( *.py )
shopt -u nullglob

if [ ${#py_files[@]} -eq 0 ]; then
    echo "[ERROR] submission 폴더에 .py 파일이 없습니다."
    exit 1
fi

mkdir -p ../output

for file in "${py_files[@]}"; do
    # 파일명에서 문제 번호 추출 (예: 1_1260.py -> 1260)
    if [[ "$file" == *_* ]]; then
        prob_num=$(echo "$file" | sed -E 's/^[0-9]+_//; s/\.py$//')
    else
        prob_num=$(echo "$file" | sed 's/\.py$//')
    fi

    input_file="../input/${prob_num}_input"
    output_file="../output/${prob_num}_output"

    if [[ -f "$input_file" ]]; then
        echo "[INFO] 실행 중: $file (입력: ${prob_num}_input)"
        python "$file" < "$input_file" > "$output_file"
    else
        echo "[ERROR] 입력 파일을 찾을 수 없음: $input_file"
        exit 1
    fi
done

# mypy 테스트 실행 및 mypy_log.txt 저장
echo "[INFO] Mypy 테스트 수행 중..."
mypy . --ignore-missing-imports > ../mypy_log.txt 2>&1 || true

# conda.yml 파일 생성
echo "[INFO] 가상환경 정보 저장 중..."
conda env export --no-builds > ../conda.yml

# 가상환경 비활성화
conda deactivate
echo "[INFO] 모든 작업이 완료되었습니다."