#!/usr/bin/env bash
if [ -n "$ZSH_VERSION" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
elif [ -n "$BASH_VERSION" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  SCRIPT_DIR="$(pwd)/scripts"
fi
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  source "$PROJECT_ROOT/.env"
  set +a
fi

export PROJECT_ROOT
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export HADOOP_HOME="/opt/homebrew/opt/hadoop/libexec"
export HADOOP_CONF_DIR="$PROJECT_ROOT/config/hadoop"

export HDFS_STORE_DIR="$PROJECT_ROOT/runtime/hdfs-store"
export HDFS_TMP_DIR="$HDFS_STORE_DIR/tmp"
export HDFS_NAMENODE_DIR="$HDFS_STORE_DIR/namenode"
export HDFS_DATANODE_DIR="$HDFS_STORE_DIR/datanode"

mkdir -p "$HDFS_TMP_DIR" "$HDFS_NAMENODE_DIR" "$HDFS_DATANODE_DIR"

export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

echo "[project-env] PROJECT_ROOT=$PROJECT_ROOT"
echo "[project-env] JAVA_HOME=$JAVA_HOME"
echo "[project-env] HADOOP_HOME=$HADOOP_HOME"
echo "[project-env] HADOOP_CONF_DIR=$HADOOP_CONF_DIR"
