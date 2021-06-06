from fastapi import FastAPI
from uuid import uuid4
from pydantic import BaseModel
from typing import List

from .blockchain import Blockchain


app = FastAPI()

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


class TransactionModel(BaseModel):
    sender: str
    recipient: str
    amount: float


class NodeModel(BaseModel):
    node: str


class NodesListModel(BaseModel):
    nodes: List[NodeModel]


@app.get('/mine')
async def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    result = {
        'message': 'New block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return result

@app.post('/transaction/new')
async def new_transaction(transaction: TransactionModel):
    index = blockchain.new_transaction(
        transaction.sender,
        transaction.recipient,
        transaction.amount,
    )
    return {'message': f'Transaction will be added to block {index}'}

@app.get('/chain')
def full_chain():
    result = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return result

@app.post('/nodes/register')
def register_nodes(nodes: NodesListModel):
    for node in nodes.nodes:
        blockchain.register_node(node.node)

    return {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

@app.get('/nodes/resolve')
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        result = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        result = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return result
