from datetime import timedelta
import time
from typing import ClassVar
import pandas as pd
from models import Fixtures, engine, session, OperationalError, StatementError, wraps, Expiries, PnlData, Bids

def mk_session(fun):
    def wrapper(*args, **kwargs):
        s = session()
        kwargs['session'] = s
        try:
            res = fun(*args, **kwargs)
        except Exception as e:
            s.rollback()
            s.close()
            raise e

        s.close()
        return res
    wrapper.__name__ = fun.__name__
    return wrapper


def retry_db(exceptions, n_retries=3, ival=1):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            exception_logged = False
            for r in range(n_retries):
                try:
                    return fun(*args, **kwargs)
                except exceptions as e:
                    if not exception_logged:
                        print(e)
                        exception_logged = True
                    else:
                        print("Retry #" + r + " after receiving exception.")

                    time.sleep(ival)
            return fun(*args, **kwargs)
        return wrapper
    return decorator


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_expiries(expiry, btc_price, rake_over, rake_under, session=None):
    try:
        insert_expiry = Expiries(
            expiry=expiry, btc_price=btc_price, rake_over=rake_over, rake_under=rake_under)
        session.add(insert_expiry)
        session.commit()
        return insert_expiry.idexpiries
    except Exception as e:
        print(e)
        return 0

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_pnldata(fixtureId, price, strike, probability, over, under, timestamp, endTime, session=None):
    try:
        insert_probability = PnlData(
            fixtureId=fixtureId, price=price, strike=strike, probability=probability, over=over, under=under, bidAmount=100, timestamp=timestamp, endTime=endTime)
        session.add(insert_probability)
        session.commit()
        return insert_probability.idpnldata
    except Exception as e:
        print(e)
        return 0

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_bids(fixtureId, price, strike, probability, over, under, timestamp, endTime, session=None):
    try:
        insert_bids = Bids(
            fixtureId=fixtureId, price=price, strike=strike, probability=probability, over=over, under=under, bidAmount=100, timestamp=timestamp, endTime=endTime)
        session.add(insert_bids)
        session.commit()
        return insert_bids.idbids
    except Exception as e:
        print(e)
        return 0

# @retry_db((OperationalError, StatementError), n_retries=3)
# @mk_session
# def db_get_expiry_data(expiry, odds_id, session=None):
#     try:
#         check_user = session.query(Expiries, Probabilities).with_entities(Expiries.expiry, Expiries.btc_price, Expiries.rake_over, Expiries.rake_under, Probabilities.odds_id, Probabilities.strike, Probabilities.over, Probabilities.under).filter(Expiries.expiry == expiry, Probabilities.odds_id == odds_id,Expiries.idexpiries == Probabilities.idexpiries).statement
#         df = pd.read_sql(check_user, engine)
#         if(df.empty):
#             return None
#         else:
#             return df.to_json(orient="records")
#     except Exception as e:
#         print(e)
#         return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_add_fixture(fixture_type, start_time, market_end_time, end_time, session=None):
    try:
        check_fixture = session.query(Fixtures).filter(Fixtures.fixtureType == fixture_type, Fixtures.startTime == start_time, Fixtures.marketEndTime == market_end_time, Fixtures.endTime == end_time).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            insert_fixture = Fixtures(fixtureType=fixture_type, startTime=start_time, marketEndTime=market_end_time, endTime=end_time)
            session.add(insert_fixture)
            session.commit()
            return insert_fixture.id

        return 0
        
    except Exception as e:
        print(e)
        return 0


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixture(fixture_time, session=None):
    try:
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime, Fixtures.status).filter(Fixtures.startTime > fixture_time, Fixtures.status == 'NOT CREATED').order_by(Fixtures.startTime.asc()).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_started_fixture(current_time, session=None):
    try:
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime, Fixtures.status).filter(
            Fixtures.startTime < current_time).order_by(Fixtures.startTime.desc()).limit(1).statement
        df = pd.read_sql(check_fixture, engine)
        
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_started_fixtures(session=None):
    try:
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime, Fixtures.status).filter(Fixtures.status == 'STARTED').order_by(Fixtures.startTime.desc()).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_last_started_fixture(current_time, session=None):
    try:
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime).filter(Fixtures.marketEndTime < current_time, Fixtures.endTime > current_time).order_by(Fixtures.startTime.asc()).limit(1).statement
        df = pd.read_sql(check_fixture, engine)
        
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_ended_fixture(current_time, session=None):
    try:
        last_time = current_time + timedelta(hours=-24)
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime, Fixtures.status).filter(Fixtures.endTime < current_time, Fixtures.endTime > last_time, Fixtures.status == 'STARTED').order_by(Fixtures.endTime.desc()).statement
        df = pd.read_sql(check_fixture, engine)
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_set_fixture_status(fixtureId, status, session=None):
    try:
        update_fixture = {"status": status}
        session.query(Fixtures).filter(Fixtures.id == fixtureId).update(update_fixture, synchronize_session=False)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_set_fixture_price(fixtureId, price, session=None):
    try:
        update_fixture = {'price': price}
        session.query(Fixtures).filter(Fixtures.id == fixtureId).update(update_fixture, synchronize_session=False)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return None

@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixture_end_price(fixtureId, session=None):
    try:
        check_price = session.query(Fixtures).with_entities(
            Fixtures.price).filter(Fixtures.id == fixtureId).statement
        df = pd.read_sql(check_price, engine)
        if(df.empty):
            return None
        else:
            end_price = df.iloc[0]['price']
            return end_price
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixtures_by_status(status, session=None):
    try:
        # print(status)
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime, Fixtures.price, Fixtures.status).filter(Fixtures.status == status).order_by(Fixtures.startTime.desc()).limit(1000).statement
        df = pd.read_sql(check_fixture, engine)
        # print(check_fixture.compile(engine))
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixtures(session=None):
    try:
        # print(status)
        check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime,Fixtures.price, Fixtures.status).order_by(Fixtures.startTime.desc()).limit(1000).statement
        df = pd.read_sql(check_fixture, engine)
        # print(check_fixture.compile(engine))
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixtures_by_id(from_fixture=None, to_fixture=None, session=None):
    try:
        if(from_fixture != None and to_fixture != None):
            check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime,  Fixtures.price, Fixtures.status).filter(Fixtures.id >= from_fixture, Fixtures.id <= to_fixture).order_by(Fixtures.startTime.desc()).statement
        elif(from_fixture != None and to_fixture == None):
            check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime,  Fixtures.price, Fixtures.status).filter(Fixtures.id >= from_fixture).order_by(Fixtures.startTime.asc()).limit(100).statement
        elif(from_fixture == None and to_fixture != None):
            check_fixture = session.query(Fixtures).with_entities(Fixtures.id, Fixtures.startTime, Fixtures.marketEndTime, Fixtures.endTime,  Fixtures.price, Fixtures.status).filter(Fixtures.id <= to_fixture).order_by(Fixtures.startTime.desc()).limit(100).statement
        df = pd.read_sql(check_fixture, engine)
        # print(check_fixture.compile(engine))
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixture_pnl_data(fixtureId, session=None):
    try:
        # print(status)
        check_fixture = session.query().with_entities(PnlData.idpnldata, PnlData.strike, PnlData.over, PnlData.under, PnlData.bidAmount).filter(PnlData.fixtureId == fixtureId).statement
        df = pd.read_sql(check_fixture, engine)
        # print(check_fixture.compile(engine))
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_update_fixture_pnl(idPnlData, price, overPnl, underPnl, session=None):
    try:
        update_pnl = {'endPrice': price, 'overPnl': overPnl, 'underPnl': underPnl}
        session.query(PnlData).filter(PnlData.idpnldata == idPnlData).update(
            update_pnl, synchronize_session=False)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_get_fixture_bid_data(fixtureId, session=None):
    try:
        # print(status)
        check_fixture = session.query().with_entities(Bids.idbids, Bids.strike, Bids.over,
                                                      Bids.under, Bids.bidAmount).filter(Bids.fixtureId == fixtureId).statement
        df = pd.read_sql(check_fixture, engine)
        # print(check_fixture.compile(engine))
        if(df.empty):
            return None
        else:
            return df.to_json(orient="records")
    except Exception as e:
        print(e)
        return None


@retry_db((OperationalError, StatementError), n_retries=3)
@mk_session
def db_update_fixture_bid(idbid, price, overPnl, underPnl, session=None):
    try:
        update_bid = {'endPrice': price, 'overPnl': overPnl, 'underPnl': underPnl}
        session.query(Bids).filter(Bids.idbids == idbid).update(
            update_bid, synchronize_session=False)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return None
